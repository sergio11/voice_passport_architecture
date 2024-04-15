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

    await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    const isValid = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);

    expect(isValid).to.be.true;
  });


  it("disable voiceID verification successfully", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    const userHash = generateHash();
    const audioHash = generateHash();

    await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    let isValidBeforeDisabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);
    await voiceIDVerifierContractInstance.connect(owner).disableVoiceIDVerification(audioHash);
    let isValidAfterDisabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);

    expect(isValidBeforeDisabling).to.be.true
    expect(isValidAfterDisabling).to.be.false
  });

  it("enable voiceID verification successfully", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    const userHash = generateHash();
    const audioHash = generateHash();

    await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    await voiceIDVerifierContractInstance.connect(owner).disableVoiceIDVerification(audioHash);
    let isValidAfterDisabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);
    await voiceIDVerifierContractInstance.connect(owner).enableVoiceIDVerification(audioHash);
    let isValidAfterEnabling = await voiceIDVerifierContractInstance.connect(owner).verifyVoiceID(userHash, audioHash);

    expect(isValidAfterDisabling).to.be.false
    expect(isValidAfterEnabling).to.be.true
  });
});