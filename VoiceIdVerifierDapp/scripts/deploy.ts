import { ethers } from "hardhat";

async function main() {
  const utilsContractFactory = await ethers.getContractFactory("Utils")
  const utilsContractInstance = await utilsContractFactory.deploy()
  const voiceIDVerifierContractFactory = await ethers.getContractFactory("VoiceIDVerifier", {
    libraries: {
      Utils: utilsContractInstance.address,
    },
  })
  const voiceIDVerifierContractInstance = await voiceIDVerifierContractFactory.deploy()
  await voiceIDVerifierContractInstance.deployed()

  console.log(`VoiceIDVerifier contract deployed to ${voiceIDVerifierContractInstance.address}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
