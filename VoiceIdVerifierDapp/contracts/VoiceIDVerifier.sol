// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./IVoiceIDVerifier.sol";
import "./Utils.sol";

contract VoiceIDVerifier is Ownable, IVoiceIDVerifier {
    using Utils for string;
    
    // Mapping to store voice ID verification information
    mapping(string => VoiceIDVerification) public voiceIDVerifications;

    // Function to register a new voice ID verification
    function registerVoiceIDVerification(string memory _userHash, string memory _audioHash) external override onlyOwner {
        // Store the voice ID verification information
        voiceIDVerifications[_userHash] = VoiceIDVerification(_userHash, _audioHash, true);

        // Emit the registration event
        emit VoiceIDVerificationRegistered(_audioHash, _userHash);
    }

    // Function to disable voice ID verification
    function disableVoiceIDVerification(string memory _userHash) external override onlyOwner {
        // Disable voice ID verification
        voiceIDVerifications[_userHash].isEnabled = false;

        // Emit the registration event
        emit VoiceIDVerificationDisabled(_userHash);
    }

    // Function to enable voice ID verification
    function enableVoiceIDVerification(string memory _userHash) external override onlyOwner {
        // Enable voice ID verification
        voiceIDVerifications[_userHash].isEnabled = true;
        
        // Emit the registration event
        emit VoiceIDVerificationEnabled(_userHash);
    }

    // Method to verify voice identity and return true if valid
    function verifyVoiceID(string memory _userHash, string memory _audioHash) external view returns (bool) {
        // Retrieve the voice ID verification information for the given user hash
        VoiceIDVerification memory voiceIDVerification = voiceIDVerifications[_userHash];
        
        // Check if the voice ID verification information exists and is enabled
        if (voiceIDVerification.audioHash.compareStrings(_audioHash) && voiceIDVerification.isEnabled) {
            // Voice authentication successful
            return true;
        } else {
            // Voice authentication failed
            return false;
        }
    }
}