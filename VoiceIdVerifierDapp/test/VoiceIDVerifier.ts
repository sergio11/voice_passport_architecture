import { expect } from "chai";
import { ethers } from "hardhat";
const { v4: uuidv4 } = require('uuid');
const CryptoJS = require("crypto-js");

describe("VoiceIDVerifier", function () {

  async function deployContractFixture() {
    const [owner, addr1, addr2] = await ethers.getSigners()
    const utilsContractFactory = await ethers.getContractFactory("Utils")
    const utilsContractInstance = await utilsContractFactory.deploy()
    const voiceIDVerifierContractFactory = await ethers.getContractFactory("VoiceIDVerifier", {
      libraries: {
        Utils: utilsContractInstance.address,
      },
    })
    const voiceIDVerifierContractInstance = await voiceIDVerifierContractFactory.deploy()
    await voiceIDVerifierContractInstance.deployed()
    return { voiceIDVerifierContractInstance, owner, addr1, addr2 }
  }

  function generateHash() {
    const uuid = uuidv4();
    return CryptoJS.SHA256(uuid).toString(CryptoJS.enc.Hex);
  }

  it("Should set the right owner", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    expect(await voiceIDVerifierContractInstance.owner()).to.equal(owner.address)
  });

  it("register voiceID verification successfully", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    const userHash = generateHash();
    const audioHash = generateHash();

    let tx = await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    let receipt = await tx.wait()
    let events = receipt.events?.map((x) => x.event)
    const isValid = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);

    expect(isValid).to.be.true;
    expect(events).not.be.null
    expect(events!![0]).to.equal("VoiceIDVerificationRegistered")
  });


  it("disable voiceID verification successfully", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    const userHash = generateHash();
    const audioHash = generateHash();

    await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    let isValidBeforeDisabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);
    let tx = await voiceIDVerifierContractInstance.connect(owner).disableVoiceIDVerification(userHash);
    let receipt = await tx.wait()
    let events = receipt.events?.map((x) => x.event)
    let isValidAfterDisabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);

    expect(isValidBeforeDisabling).to.be.true
    expect(isValidAfterDisabling).to.be.false
    expect(events).not.be.null
    expect(events!![0]).to.equal("VoiceIDVerificationDisabled")
  });

  it("enable voiceID verification successfully", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    const userHash = generateHash();
    const audioHash = generateHash();

    await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    await voiceIDVerifierContractInstance.connect(owner).disableVoiceIDVerification(userHash);
    let isValidAfterDisabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);
    let tx = await voiceIDVerifierContractInstance.connect(owner).enableVoiceIDVerification(userHash);
    let receipt = await tx.wait()
    let events = receipt.events?.map((x) => x.event)
    let isValidAfterEnabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);

    expect(isValidAfterDisabling).to.be.false
    expect(isValidAfterEnabling).to.be.true
    expect(events).not.be.null
    expect(events!![0]).to.equal("VoiceIDVerificationEnabled")
  });

  it("only the contract's owner can register and verify voice ids", async function () {
    const { voiceIDVerifierContractInstance, addr1 } = await deployContractFixture()
    const userHash = generateHash();
    const audioHash = generateHash();

    var errorMessage: Error | null = null
    try {
      await voiceIDVerifierContractInstance.connect(addr1).registerVoiceIDVerification(userHash, audioHash);
      await voiceIDVerifierContractInstance.connect(addr1).verifyVoiceID(userHash, audioHash);
    } catch(error) {
      if (error instanceof Error) {
        errorMessage = error
      }
    }

    expect(errorMessage).not.be.null
    expect(errorMessage!!.message).to.contain("Ownable: caller is not the owner")
  });
});