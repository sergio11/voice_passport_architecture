// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./IVoiceIDVerifier.sol";

contract VoiceIDVerifier is Ownable, IVoiceIDVerifier {
    
    // Mapping to store voice ID verification information
    mapping(string => VoiceIDVerification) public voiceIDVerifications;

    // Constructor to initialize the contract
    constructor() Ownable(msg.sender) {}

    // Function to register a new voice ID verification
    function registerVoiceIDVerification(string memory _userHash, string memory _audioHash) external override onlyOwner {
        // Store the voice ID verification information
        voiceIDVerifications[_audioHash] = VoiceIDVerification(_userHash, _audioHash, true);

        // Emit the registration event
        emit VoiceIDVerificationRegistered(_audioHash, _userHash);
    }

    // Function to disable voice ID verification
    function disableVoiceIDVerification(string memory _audioHash) external override onlyOwner {
        // Disable voice ID verification
        voiceIDVerifications[_audioHash].isEnabled = false;
    }

    // Function to enable voice ID verification
    function enableVoiceIDVerification(string memory _audioHash) external override onlyOwner {
        // Enable voice ID verification
        voiceIDVerifications[_audioHash].isEnabled = true;
    }

    // Function to verify voice ID and return the user hash if valid
    function verifyVoiceID(string memory _audioHash) external view override returns (string memory) {
        // Check if voice ID verification is enabled
        require(voiceIDVerifications[_audioHash].isEnabled, "Voice ID verification is disabled");

        // Return the user hash associated with the audio hash
        return voiceIDVerifications[_audioHash].userHash;
    }
}