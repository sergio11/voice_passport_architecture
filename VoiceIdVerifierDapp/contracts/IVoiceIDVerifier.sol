// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

interface IVoiceIDVerifier { 

    // Method to register a voice identity verification
    function registerVoiceIDVerification(string memory _userHash, string memory _audioHash) external;

    // Method to disable voice identity verification
    function disableVoiceIDVerification(string memory _userHash) external;

    // Method to enable voice identity verification
    function enableVoiceIDVerification(string memory _userHash) external;

    // Method to verify voice identity and return the user hash if valid
    function verifyVoiceID(string memory _audioHash) external view returns (string memory);

    // Event emitted when a new voice identity verification is registered
    event VoiceIDVerificationRegistered(
        string indexed audioHash, 
        string indexed userHash
    );

    // Struct to store voice identity verification information
    struct VoiceIDVerification {
        string userHash;
        string audioHash;
        bool isEnabled;
    }
}