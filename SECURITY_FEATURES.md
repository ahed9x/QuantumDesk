# QuantumDesk Security Features

## 🔐 App Lock Protection

QuantumDesk includes robust application lock functionality to protect unauthorized access to your system tools.

### Features:
- **PIN Lock**: Set a 4-8 digit PIN to secure the application
- **Password Lock**: Set a secure password (minimum 6 characters) 
- **Secure Storage**: Credentials are hashed using SHA-256 for security
- **Easy Management**: Enable, disable, or change locks through the GUI

### Usage:
1. Navigate to the **Security** panel
2. Find the **🔐 App Lock Protection** section
3. Choose either "Set PIN Lock" or "Set Password Lock"
4. Enter your chosen PIN/password when prompted
5. The lock will be activated immediately

### Security Notes:
- Credentials are stored securely in `~/.quantumdesk/security_config.json`
- All passwords/PINs are hashed before storage
- The app will remember your lock preference between sessions

---

## 📁 Encrypted Task Storage

Protect your saved tasks and automation configurations with military-grade encryption.

### Features:
- **AES Encryption**: Uses Fernet symmetric encryption (AES 128)
- **Password Protection**: Encryption keys derived from user passwords
- **Export/Import**: Securely share task configurations
- **Automatic Encryption**: All tasks encrypted when feature is enabled

### Setup:
1. Navigate to the **Security** panel
2. Find the **📁 Encrypted Task Storage** section
3. Click "Enable Encryption"
4. Set an encryption password (minimum 6 characters)
5. All future task saves will be encrypted

### Export/Import Tasks:
- **Export**: Save encrypted task configurations to `.qtask` files
- **Import**: Load encrypted task configurations from `.qtask` files
- **Sharing**: Safely share task configurations with others

### Security Specifications:
- **Encryption**: Fernet (AES 128 in CBC mode with HMAC SHA256)
- **Key Derivation**: PBKDF2 with SHA256 (100,000 iterations)
- **File Format**: Custom `.qtask` format with encrypted JSON
- **Storage**: Encryption keys stored in `~/.quantumdesk/task_encryption.key`

---

## 🛡️ Security Best Practices

### Recommended Security Setup:
1. **Enable App Lock**: Set a strong PIN or password
2. **Enable Task Encryption**: Protect your automation configurations
3. **Regular Exports**: Backup your encrypted tasks regularly
4. **Secure Storage**: Keep encryption passwords in a secure location

### Password Guidelines:
- Use unique, strong passwords for encryption
- Combine letters, numbers, and symbols
- Don't reuse passwords from other applications
- Consider using a password manager

### File Security:
- `.qtask` files are fully encrypted and safe to store/share
- Configuration files in `~/.quantumdesk/` contain sensitive data
- Keep backup copies of important configurations

---

## 🔧 Technical Implementation

### App Lock System:
```python
# PIN/Password Storage Format
{
    "app_lock": {
        "type": "pin" | "password",
        "hash": "sha256_hash_of_credential",
        "enabled": true | false
    }
}
```

### Encryption System:
```python
# Encryption Configuration
{
    "encryption_enabled": true | false,
    "key_hash": "sha256_hash_of_derived_key"
}
```

### Dependencies:
- `cryptography`: For Fernet encryption
- `hashlib`: For credential hashing
- `json`: For configuration storage

---

## ⚠️ Important Notes

### Data Recovery:
- **Lost Passwords**: No password recovery option available
- **Backup Keys**: Store encryption passwords securely
- **Export Regularly**: Create backups of important configurations

### Compatibility:
- Encrypted tasks are only compatible with QuantumDesk
- `.qtask` files require the same encryption password
- Cross-platform compatible (Windows/Linux/macOS)

### Performance:
- Minimal impact on application performance
- Encryption/decryption happens only during save/load
- Real-time operations are not affected

---

## 🚀 Future Enhancements

Planned security features for future releases:
- **Multi-factor Authentication**: SMS/Email verification
- **Biometric Lock**: Fingerprint/Face recognition
- **Encrypted Database**: Full database encryption
- **Audit Logging**: Security event tracking
- **Password Recovery**: Secure recovery mechanisms
- **Session Management**: Automatic logout after inactivity

---

## 📞 Support

For security-related questions or issues:
1. Check the application logs in the **Logs** panel
2. Verify encryption library installation: `pip install cryptography`
3. Ensure configuration files have proper permissions
4. Contact support with specific error messages

Remember: Security is a shared responsibility - always follow best practices for password management and data protection.
