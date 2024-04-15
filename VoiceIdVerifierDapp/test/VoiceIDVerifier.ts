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

  it("Should set the right owner", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    expect(await voiceIDVerifierContractInstance.owner()).to.equal(owner.address)
  });

  it("register voiceID verification successfully", async function () {
    const { voiceIDVerifierContractInstance, owner } = await deployContractFixture()
    // Generate UUID for the user and for the audio
    const userUUID = uuidv4();
    const audioUUID = uuidv4();

    // Generate hashes for the user and the audio
    const userHash = CryptoJS.SHA256(userUUID).toString(CryptoJS.enc.Hex);
    const audioHash = CryptoJS.SHA256(audioUUID).toString(CryptoJS.enc.Hex);

    // Register voice identity verification
    let tx = await voiceIDVerifierContractInstance.connect(owner).registerVoiceIDVerification(userHash, audioHash);
    let receipt = await tx.wait()
    let events = receipt.events?.map((x) => x.event)

    expect(events).to.be.an('array').that.is.not.empty
    expect(events!![0]).to.equal("VoiceIDVerificationRegistered")
    expect(await voiceIDVerifierContractInstance.owner()).to.equal(owner.address)
  });
});