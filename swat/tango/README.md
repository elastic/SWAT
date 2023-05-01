# Tango Payload
SWAT's Tango payload was developed in GoLang, making it compatible across platforms. Tango is a malicious command-and-control (C2) payload that can be built and distributed to any Windows, Linux or macOS endpoint of choosing. A GCP service account, credentials and specific Google Workspace APIs must be enabled for the payload to operate successfully.

#### Setup Credentials and Enable APIs
1. Setup a service account for Tango in GCP
2. Create credentials for the Tango service account
3. Enable the following Google Workspace APIs for the Tango service account:
   1. Drive API
   2. Sheets API
   3. Docs API
   4. GMail API
   5. Apps Script API

#### Build the Executable from Go

```
cd swat/tango
go build
```

#### Execute Tango Executable
The executable can be executed on the endpoint after distribution. Credentials can be passed into the execution command or can be hardcoded into the binary itself.

Windows
```
TBD
```

Linux
```
TBD
```

macOS
```
TBD
```