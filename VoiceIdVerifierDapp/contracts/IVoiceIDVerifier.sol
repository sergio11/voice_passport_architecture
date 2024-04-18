// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

interface IVoiceIDVerifier { 

    // Method to register a voice identity verification
    function registerVoiceIDVerification(string memory _userHash, string memory _audioHash) external;

    // Method to disable voice identity verification
    function disableVoiceIDVerification(string memory _userHash) external;

    // Method to enable voice identity verification
    function enableVoiceIDVerification(string memory _userHash) external;

    // Method to verify voice identity and return true if valid
    function verifyVoiceID(string memory _userHash, string memory _audioHash) external view returns (bool);

    // Event emitted when a new voice identity verification is registered
    event VoiceIDVerificationRegistered(
        string indexed audioHash, 
        string indexed userHash
    );

    // Event emitted when voice identity verification is enabled for a user
    event VoiceIDVerificationEnabled(
        string indexed userHash
    );

    // Event emitted when voice identity verification is disabled for a user
    event VoiceIDVerificationDisabled(
        string indexed userHash
    );

    // Struct to store voice identity verification information
    struct VoiceIDVerification {
        string userHash;
        string audioHash;
        bool isEnabled;
    }
}