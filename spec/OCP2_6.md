<!-- page 1 -->
# Datacenter NVMe® SSD Specification

Version 2.6 (09252024)

Author: Ross Stenfort, Meta
Author: Lee Prewitt, Microsoft
Author: Paul Kaler, HPE
Author: David Black, Austin Bolen, Dell Technologies
Author: Chris Sabol, Charles Kunzman, Google

<!-- page 2 -->
## Table of Contents

1 OCP ....................................................................................................................................................................................... 8

1.1 License OWF Option ................................................................................................................................................... 8

1.2 System Firmware ........................................................................................................................................................ 8

2 Overview............................................................................................................................................................................ 8

3 Scope ................................................................................................................................................................................... 8

4 NVM Express Requirements ...................................................................................................................................... 9

4.1 Overview ......................................................................................................................................................................... 9

4.2 NVMe Reset Supported ............................................................................................................................................. 9

4.3 NVMe Controller Configuration and Behavior ................................................................................................ 9

4.4 NVMe Admin Command Set .................................................................................................................................. 10

4.4.1 Namespace Management/Attachment Commands ............................................................................................ 12

4.4.2 Namespace Utilization (NUSE) .................................................................................................................................... 13

4.4.3 UUID for DSSD Specific Information ......................................................................................................................... 13

4.5 NVMe I/O Command Set......................................................................................................................................... 15

4.6 Optional NVMe Feature Support ......................................................................................................................... 16

4.7 Command Timeout ................................................................................................................................................... 17

4.8 Log Page Requirements .......................................................................................................................................... 17

4.8.1 Standard Log Page Requirements .............................................................................................................................. 17

4.8.2 TCG Activity Events for Persistent Event Log ....................................................................................................... 20

4.8.3 TCG Activity Event Format ............................................................................................................................................ 22

4.8.4 DSSD Log Page Requirements ..................................................................................................................................... 24

4.8.5 SMART / Health Information Requirements ......................................................................................................... 25

4.8.6 SMART / Health Information Extended (Log Identifier C0h) ......................................................................... 26

4.8.7 Error Recovery (Log Identifier C1h) ......................................................................................................................... 37

4.8.8 Latency Monitor Log Page and Feature Set Requirements ............................................................................. 44

4.8.9 Latency Monitor (Log Identifier C3h) ...................................................................................................................... 45

4.8.10 Device Capabilities (Log Identifier C4h) Requirements ................................................................................. 59

4.8.11 DSSD Power State Requirements ............................................................................................................................ 62

4.8.12 Unsupported Requirements (Log Identifier C5h) ............................................................................................ 63

4.8.13 Hardware Component (Log Identifier C6h) ........................................................................................................ 64

4.8.14 TCG Configuration (Log Identifier C7h) ................................................................................................................ 66

4.8.15 Telemetry String (Log Identifier C9h) ................................................................................................................... 71

4.9 Host and Controller Initiated Telemetry Log Pages .................................................................................... 78

<!-- page 3 -->
4.9.1 Theory of Operation ........................................................................................................................................................ 78

4.9.2 Data Partitioning Overview .......................................................................................................................................... 78

4.9.3 Statistic Area ....................................................................................................................................................................... 79

4.9.4 Event FIFO ........................................................................................................................................................................... 79

4.9.5 Existing NVMe Log Pages ............................................................................................................................................... 79

4.9.6 Debug Structure Overview Summary ....................................................................................................................... 79

4.9.7 Telemetry Data Requirements .................................................................................................................................... 80

4.9.8 Telemetry Reason Identifier Format ........................................................................................................................ 82

4.9.9 Debug Profiles .................................................................................................................................................................... 83

4.9.10 Statistic Descriptor ........................................................................................................................................................ 83

4.9.11 Statistic Identifiers......................................................................................................................................................... 84

4.9.12 Statistic Descriptor Location ..................................................................................................................................... 94

4.9.13 Statistic Requirements ................................................................................................................................................. 96

4.9.14 Event FIFO Requirements ..................................................................................................................................... 96

4.9.15 Event FIFO Location ................................................................................................................................................... 112

4.9.16 Telemetry Data Area ............................................................................................................................................ 113

4.10 Device Self-test Requirements ....................................................................................................................... 120

4.11 Firmware Update Requirements ................................................................................................................... 122

4.12 Factory Default Requirements ....................................................................................................................... 125

4.13 Deallocation Requirements ............................................................................................................................. 126

4.14 Sector Size and Namespace Support ........................................................................................................... 126

4.15 Set/Get Features Requirements .................................................................................................................... 126

4.15.1 General Feature Requirements ............................................................................................................................. 127

4.15.2 DSSD Feature Requirements .................................................................................................................................. 128

4.15.3 Error Injection (Feature Identifier C0h) Set Features ................................................................................. 128

4.15.4 Error Injection (Feature Identifier C0h) Get Features ................................................................................. 131

4.15.5 PLP Failure Mode (Feature Identifier C2h) Set Features ........................................................................... 132

4.15.6 PLP Failure Mode (Feature Identifier C2h) Get Features ........................................................................... 133

4.15.7 Clear PCIe Correctable Error Counters (Feature Identifier C3h) Set Features ................................. 134

4.15.8 Clear PCIe Correctable Error Counters (Feature Identifier C3h) Get Features ................................. 135

4.15.9 Enable IEEE1667 Silo (Feature Identifier C4h) Set Features ................................................................... 135

4.15.10 Enable IEEE1667 Silo (Feature Identifier C4h) Get Features ................................................................ 136

4.15.11 Latency Monitor (Feature Identifier C5h) Set Features ........................................................................... 137

4.15.12 Latency Monitor (Feature Identifier C5h) Get Features ........................................................................... 139

4.15.13 PLP Health Check Interval (Feature Identifier C6h) Set Features ....................................................... 140

<!-- page 4 -->
4.15.14 PLP Health Check Interval (Feature Identifier C6h) Get Features ....................................................... 140

4.15.15 DSSD Power State (Feature Identifier C7h) Set Features ........................................................................ 141

4.15.16 DSSD Power State (Feature Identifier C7h) Get Features........................................................................ 142

4.15.17 Telemetry Profile (Feature Identifier C8h) Set Features ......................................................................... 143

4.15.18 Telemetry Profile (Feature Identifier C8h) Get Features ........................................................................ 144

4.15.19 DSSD Asynchronous Event Configuration (Feature Identifier C9h) Set Features ......................... 144

4.15.20 DSSD Asynchronous Event Configuration (Feature Identifier C9h) Get Features ........................ 146

5 PCIe Requirements ................................................................................................................................................... 147

5.1 Boot Requirements ................................................................................................................................................ 150

5.2 PCIe Error Logging ................................................................................................................................................. 150

5.3 Low Power Modes .................................................................................................................................................. 150

5.4 PCIe Eye Capture .................................................................................................................................................... 150

6 Optional Device Features ............................................................................................................................................. 151

6.1 Flexible Data Placement Requirements ........................................................................................................ 151

6.1.1 Generic Flexible Data Placement Requirements ............................................................................................... 151

6.1.2 FDP Single Reclaim Group Configuration ............................................................................................................ 151

6.1.3 FDP Die Placement Configuration ........................................................................................................................... 151

6.2 DIX Requirements .................................................................................................................................................. 151

7 Reliability ..................................................................................................................................................................... 152

7.1 Uncorrectable Bit Error Rate ............................................................................................................................. 152

7.2 Power On/Off Requirements ............................................................................................................................. 152

7.2.1 Time to Ready and Shutdown Requirements..................................................................................................... 152

7.2.2 Incomplete/Unsuccessful Shutdown ..................................................................................................................... 153

7.3 End to End Internal Data Protection .............................................................................................................. 155

7.4 Behavior on Firmware Crash, Panic or Assert ........................................................................................... 156

7.5 Annual Failure Rate (AFR) .................................................................................................................................. 156

7.6 Background Data Refresh ................................................................................................................................... 157

7.7 Wear-leveling ........................................................................................................................................................... 157

7.8 Power Loss Protection ......................................................................................................................................... 157

7.9 Device Limits ............................................................................................................................................................ 160

8 Endurance .................................................................................................................................................................... 160

8.1 Endurance Data ....................................................................................................................................................... 160

8.2 Retention Conditions ............................................................................................................................................ 160

8.3 Shelf Life ..................................................................................................................................................................... 161

8.4 End-of-Life (EOL) ................................................................................................................................................... 161

<!-- page 5 -->
9 Thermal ......................................................................................................................................................................... 162

9.1 Data Center Altitude .............................................................................................................................................. 162

9.2 Thermal Throttling ................................................................................................................................................ 163

9.3 Temperature Reporting ....................................................................................................................................... 164

9.4 Thermal Shutdown ................................................................................................................................................ 165

10 Form Factor Requirements ................................................................................................................................... 165

10.1 Generic Form Factor Requirements............................................................................................................. 165

10.2 Power Consumption Measurement Methodology ................................................................................. 165

10.3 Power Levels ......................................................................................................................................................... 166

10.4 M.2 Form Factor Requirements ..................................................................................................................... 166

10.5 E1.S Form Factor Requirements.................................................................................................................... 167

10.6 E1.L Form Factor Requirements ................................................................................................................... 168

10.7 E3 Form Factor Requirements ....................................................................................................................... 168

10.8 SFF-8639 (U.2/U.3) Form Factor Requirements .................................................................................... 169

11 Management Support .............................................................................................................................................. 169

11.1 NVMe Basic Management Command (Appendix A) Requirements ................................................ 169

11.2 NVMe Basic Management Command (Appendix A) Data Format ................................................... 170

11.3 NVMe-MI Requirements ................................................................................................................................... 174

11.4 VPD Requirements .............................................................................................................................................. 177

12 Security ......................................................................................................................................................................... 177

12.1 Basic Security Requirements .......................................................................................................................... 177

12.2 Secure Boot ............................................................................................................................................................ 181

12.3 DMTF Security Protocol and Data Model (SPDM) .................................................................................. 182

12.3.1 SPDM Certificates ........................................................................................................................................................ 184

12.3.2 SPDM Firmware Measurements ........................................................................................................................... 185

12.4 Data Encryption and Eradication .................................................................................................................. 186

12.5 TCG Implementation Requirements ............................................................................................................ 186

12.6.1 TCG Version and Features ....................................................................................................................................... 187

12.6.2 TCG Communication Layer ...................................................................................................................................... 187

12.6.3 TCG Session Layer ....................................................................................................................................................... 188

12.6.4 TCG Transactions ........................................................................................................................................................ 188

12.6.5 TCG Authentication .................................................................................................................................................... 188

12.6.6 TCG Crypto ..................................................................................................................................................................... 189

12.6.7 TCG Locking Security Provider .............................................................................................................................. 189

12.6.8 TCG PSID Feature Set ................................................................................................................................................. 189

<!-- page 6 -->
13 Device Profiles ............................................................................................................................................................ 190

14 Labeling ......................................................................................................................................................................... 191

14.1 Label Requirements ............................................................................................................................................ 192

15 Compliance .................................................................................................................................................................. 196

15.1 ROHS Compliance ................................................................................................................................................ 196

15.2 ESD Compliance ................................................................................................................................................... 196

15.3 EMC Compliance .................................................................................................................................................. 196

16 Shock and Vibration ................................................................................................................................................. 196

17 Sustainability Requirements ................................................................................................................................ 197

18 Linux NVMe-CLI Plug-In Requirements .......................................................................................................... 197

18.1 NVMe-CLI Management Utility ...................................................................................................................... 197

18.2 NVMe-CLI Plugin Requirements .................................................................................................................... 197

18.2.1 NVMe-CLI Plug-In Nomenclature/Functional Requirements ................................................................... 198

18.2.2 NVMe-CLI Plug-In FW Activation History Requirements ........................................................................... 198

19 Revision History ........................................................................................................................................................ 198

20 META Specific Items ................................................................................................................................................ 198

20.1 Configuration Specifics ................................................................................................................................. 198

20.2 Performance Requirements ........................................................................................................................ 199

20.3 Performance Targets for Data-Drive QOS workloads .......................................................................... 200

20.4 Performance Targets for Boot-Drive QOS workloads ...................................................................... 201

20.5 Trim Rate Targets ................................................................................................................................................ 202

20.6 IO.go Benchmark Targets ................................................................................................................................. 202

20.7 Fileappend Benchmark Targets..................................................................................................................... 202

20.8 Sequential Write Bandwidth ........................................................................................................................... 203

20.9 CacheBench Targets ........................................................................................................................................... 203

20.10 BootBench Target ............................................................................................................................................. 203

21 Microsoft Specific Items ......................................................................................................................................... 203

21.1 Configuration Specifics ................................................................................................................................. 204

22 Latency Monitoring Feature Set Theory of Operation ............................................................................... 204

22.1 Overview ............................................................................................................................................................. 204

22.2 Functional Operation ..................................................................................................................................... 204

22.2.1 Latency Monitoring Feature Description .......................................................................................................... 204

22.2.2 Bucket Description Overview ................................................................................................................................ 204

22.2.3 Active Bucket Description ....................................................................................................................................... 204

22.2 Persistence Across Power Cycles ............................................................................................................. 210

<!-- page 7 -->
22.3 Debug Logs ......................................................................................................................................................... 210

22.4 Latency Monitoring Feature - Challenging Event Handling........................................................... 211

22.4.1 Power Off/On When Latency Monitoring Feature is Enabled .................................................................. 211

22.4.2 Power Off/On When Latency Monitoring Feature is Disabled ................................................................. 211

22.4.3 Moving Information from Active to Static Buckets ....................................................................................... 211

22.4.4 Firmware Update ........................................................................................................................................................ 211

22.5 Configuring Latency Monitoring ............................................................................................................... 211

<!-- page 8 -->
## **1 OCP**

### **1.1 License OWF Option**

Contributions to this Specification are made under the terms and conditions set forth in Open Web
Foundation Contributor License Agreement (“OWF CLA 1.0”) (“Contribution License”) by:

Meta
Microsoft
HPE
Dell Technologies
Google

Usage of this Specification is governed by the terms and conditions set forth in the Open Web Foundation
Final Specification Agreement (“OWFa 1.0”).

**Note** : The following clarifications, which distinguish technology licensed in the Contribution License
and/or Specification License from those technologies merely referenced (but not licensed), were accepted
by the Incubation Committee of the OCP:

NONE

### **1.2 System Firmware**

All products seeking OCP Accepted™ Product Recognition must complete the Open System Firmware (OSF)
[Tab in the 2021 Supplier Requirements Checklist. The completed checklist shall be uploaded and available](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1pag0tn5uBO-S-hSmEr_tXWHkCtZRqOugeg1L6vkMe6A%2Fcopy&data=04%7C01%7Cleprewit%40microsoft.com%7Ca28d333b69194fade42708d91979a598%7C72f988bf86f141af91ab2d7cd011db47%7C1%7C0%7C637568832565130990%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C1000&sdata=%2F1CEN%2Fi6XobCmANoF97asflcYwy%2FH5KMh6wHfIw3Bvk%3D&reserved=0)
at: _https://github.com/opencomputeproject/OpenSystemFirmware/[vendor_name]/[product_name]/_ .

Note to author: replace [vendor_name] and [product_name] with actual company name and product
identifier.

## **2 Overview**

This document is to define the requirements for a Datacenter NVMe SSD (DSSD) for use in datacenters.

## **3 Scope**

This document covers PCIe-attached SSDs using NVM Express.

<!-- page 9 -->
## **4 NVM Express Requirements**

### **4.1 Overview**

|Requirement ID|Description|
|---|---|
|NVMe-1|The device shall comply with all required features of the NVM Express Base Specification<br>Revision 2.0e, the NVM Express NVM Command Set Specification Revision 1.0e, and the<br>NVM Express NVMe over PCIe Transport Specification Revision 1.0e, or later except as<br>overridden by this specification. Optional features in those three specifications shall be<br>implemented per the requirements of this specification. The vendor shall provide an<br>NVMe compliance report that demonstrates compliance.|
|NVMe-2|Any optional NVMe features supported by the device not described in this document shall<br>be clearly documented and disclosed to the customer.|
|NVMe-3|Any vendor unique features supported by the device not described in this document shall<br>be clearly documented and disclosed to the customer.|

### **4.2 NVMe Reset Supported**

|Requirement ID|Description|
|---|---|
|NVMeR-1|NVM Subsystem Reset (NSSR) shall be supported via the NSSRC register.|
|NVMeR-2|NVMe Controller Reset (CC.EN cleared to 0b) shall be supported.|

### **4.3 NVMe Controller Configuration and Behavior**

|Requirement ID|Description|
|---|---|
|NVMe-CFG-1|The default arbitration shall be Round-Robin. Weighted Round Robin with Urgent Class<br>Priority shall be supported.|
|NVMe-CFG-2|The device shall support a Maximum Data Transfer Size (MDTS) value of at least 256 KiB.|
|NVMe-CFG-3|The device firmware shall support the reporting of CSTS.CFS.|
|NVMe-CFG-4|Obsolete. Replaced byLABL-11.|
|<br>NVMe-CFG-5|<br>The minimum supported queue depth shall be 1,024 per submission queue.|
|NVMe-CFG-6|The minimum number of I/O Queue Pairs shall be 1,024.|
|NVMe-CFG-7|The single default namespace (seeSECTOR-3) shall have a unique non-zero value in the<br>EUI64 (Extended Unique Identifier) field in the Identify Namespace data structure.<br>For each namespace that is created other than the initial namespace configured in the<br>factory, the device shall clear the EUI64 field in the Identify Namespace data structure to<br>0h.|
|NVMe-CFG-8|The device shall support a non-zero NGUID per Namespace that is never reused (i.e., the<br>UIDREUSE bit in the Common Namespace Features field of the Identify Namespace data<br>structure shall be set to 1b).|
|NVMe-CFG-9|The Doorbell Stride field in the Controller Capabilities data structure (CAP.DSTRD) shall be<br>cleared to 0h.|
|NVMe-CFG-10|The device shall align the start of the Doorbells to a 4096-byte boundary as per the PCI<br>Express Base Specification and the NVM Express Base Specification.|
|NVMe-CFG-11|If the Controller Memory Buffer (CMB) is supported, then the implementation shall comply<br>with TP4054. This includes the requirement that the CMB shall be disabled by default.|

<!-- page 10 -->
|Requirement ID|Description|
|---|---|
|NVMe-CFG-12|The Controller Power Scope field in the Controller Capabilities property shall be set to a<br>value of 11b to indicate it is NVM subsystem scope (i.e., the NVM subsystem does not<br>support multiple domains).|
|NVMe-CFG-13|The device shall support the NVM Command Set (i.e., in the Command Sets Supported<br>field in the Controller Capabilities (CAP) property bit 0 shall be set to 1b, bit 6 shall be<br>cleared to 0b, and bit 7 shall be cleared to 0b, and the Controller Type field in the Identify<br>Controller data structure shall be set to 01h).|
|NVMe-CFG-14|The device shall support a maximum Submission Queue Entry Size of 64 bytes (i.e., bits 7:4<br>of the SQES field in the Identify Controller data structure shall be set to 6).|
|NVMe-CFG-15|The device shall support a maximum Completion Queue Entry Size of 16 bytes (i.e., bits 7:4<br>of the CQES field in the Identify Controller data structure shall be set to 4).|
|NVMe-CFG-16|The device shall clear the Memory Page Size Minimum (MPSMIN) field to 0h (4 KiB<br>minimum page size).|
|NVMe-CFG-17|The device shall set the Memory Page Size Maximum (MPSMAX) field to a value of 1h or<br>greater (8 KiB or greater maximum page size).|
|NVMe-CFG-18|The device shall support 256 Error Log Page Entries.|
|NVMe-CFG-19|The device shall clear the Host Memory Buffer Minimum Size field and the Host Memory<br>Buffer Preferred Size field in the Identify Controller data structure to 0h (i.e., the Host<br>Memory Buffer feature shall not be supported).|
|NVMe-CFG-20|The device shall clear the CAP.CRMS.CRIMS bit to 0b.|

### **4.4 NVMe Admin Command Set**

The device shall support the following mandatory and optional NVMe Admin commands:

|Requirement ID|Description|
|---|---|
|NVMe-AD-1|The device shall support all mandatory NVMe Admin commands.|
|NVMe-AD-2|Identify – In addition to supporting all the mandatory CNS values and the associated<br>mandatory fields within the CNS, the following optional fields in the CNS shall be<br>supported:<br>• <br>Format progress indicator (FPI) with an update granularity of 1% in the Identify<br>Namespace data structure in the NVM Command Set and in the I/O Command Set<br>Independent Identify Namespace data structure.<br>• <br>I/O Performance and Endurance Hints:<br>`o` bit 4 (OPTPERF) shall be set to 1b in the Namespace Features (NSFEAT) field in<br>the Identify Namespace data structure for the NVM Command Set.|
|NVMe-AD-3|Namespace Management command shall be supported.|
|NVMe-AD-4|Namespace Attachment command shall be supported.|
|NVMe-AD-5|Format NVM command shall be supported. Secure Erase Settings (SES) values 000b, 001b<br>and 010b shall be supported.|
|NVMe-AD-6|The device shall support the NVMe-MI Receive and NVMe-MI Send commands (i.e., bit 6 in<br>the Optional Admin Command Support field in the Identify Controller data structure shall<br>be set to 1b). The device shall support all NVMe-MI commands that map to the NVMe-MI<br>Receive command and are mandatory using the in-band tunneling mechanism. The device<br>shall prohibit all NVMe-MI commands that map to the NVMe-MI Send command.|

<!-- page 11 -->
|Requirement ID|Description|
|---|---|
|NVMe-AD-7|The device shall support the Sanitize command. Block Erase (010b), Overwrite (011b), and<br>Crypto Erase (100b) sanitize operations shall be supported.|
|NVMe-AD-8|Once data is purged (seeSEC-43) due to:<br>• <br>a Sanitize command that has the No-Deallocate After Sanitize bit cleared to 0b;<br>• <br>a Sanitize command that has the No-Deallocate After Sanitize bit set to 1b but a<br>deallocate was performed due to TP4152 not being supported (see NVMe-AD-19);<br>• <br>a Format NVM command that specifies User Data Erase or Cryptographic Erase; or<br>• <br>a TCG Revert method, RevertSP method or GenKey method,<br>the device shall deallocate all user data, enable reads to the purged/deallocated LBAs<br>without generating errors, and return all zeroes for host reads to LBAs that have not been<br>written since the last such purge completed. If the requested Sanitize operation was<br>Overwrite (011b), the device shall return the bytes written by the last overwrite pass.|
|NVMe-AD-9|Obsolete. Incorporated intoNVMe-AD-8.|
|NVMe-AD-10|The device shall support Identify command UUID List functionality (CNS value 17h).|
|NVMe-AD-11|If the Namespace Identifier (NSID) is not used for a specific NVMe Admin command, and<br>the host specifies a non-zero NSID, then the controller shall abort the command with<br>status Invalid Field in Command.|
|NVMe-AD-12|The Device Self-test command shall be supported.|
|NVMe-AD-13|Obsolete.  SeeSELFTST-8.|
|<br>NVMe-AD-14|<br>The device shall support the Lockdown command.  For device profile specific<br>requirements seeDP-CFG-11.|
|NVMe-AD-15|<br>The Lockdown command shall support locking down all supported Admin commands on<br>the in-band interface including the Lockdown command itself and all Admin commands<br>not referenced in this specification.|
|NVMe-AD-16|The Lockdown command shall support locking down all supported Features on the in-band<br>interface, including those not referenced in this specification.|
|NVMe-AD-17|The device shall set the No-Deallocate Modifies Media After Sanitize field in the Sanitize<br>Capabilities in the Identify Controller data structure to 01b. Additional media modification<br>after Sanitize is prohibited.|
|NVMe-AD-18|The device shall clear the No-Deallocate Inhibited bit in the Sanitize Capabilities in the<br>Identify Controller data structure to 0b.|
|NVMe-AD-19|If the device cannot return logical block data due to checksum errors after a sanitize<br>operation successfully completes that had been started by a Sanitize command with the<br>No-Deallocate After Sanitize bit set to 1b (e.g., TP4152 is not supported but see NVMe-AD-<br>26), then the device shall instead perform a deallocation even though it was requested not<br>to deallocate and shall set the Sanitize Status field to 100b in the Sanitize Status log page <br>upon successful completion of the Sanitize operation and deallocation. This behavior<br>overrides the requirements in the NVM Express Base Specification.|
|NVMe-AD-20|Obsolete. Incorporated intoNVMe-AD-8.|
|<br>NVMe-AD-21|<br>The device shall not write data to any namespace user data in the NVM subsystem as part<br>of a Crypto Erase sanitize operation, Block Erase sanitize operation, Format NVM<br>Cryptographic Erase, Format NVM User Data Erase, or TCG Opal Revert/RevertSP/GenKey<br>method.|

<!-- page 12 -->
|Requirement ID|Description|
|---|---|
|NVMe-AD-22|The device shall be shipped from the factory with the Sanitize Status field in the Sanitize<br>Status log page cleared to 000b indicating the NVM subsystem has never been sanitized<br>and the Global Data Erased bit in the Sanitize Status field set to 1b.|
|NVMe-AD-23|The device shall support the Format NVM command on a per namespace basis (i.e., bit 0<br>and bit 1 of the Format NVM Attributes field in Identify Controller shall be cleared to 00b).|
|NVMe-AD-24|The device shall report a minimum of 4 in the Asynchronous Event Request Limit field in<br>the Identify Controller data structure.|
|NVMe-AD-25|If asynchronous events occur for which reporting is enabled and there are no<br>Asynchronous Event Request commands outstanding, the controller shall retain the event<br>information for those Asynchronous Event Types and use that information for responses to<br>future Asynchronous Event Request commands. Queued duplicate Asynchronous events<br>shall be reported once.|
|NVMe-AD-26|The device shall support Sanitize Media Verification per TP4152.|
|NVMe-AD-27|The device is not required to support the Get LBA Status command. The device shall<br>support the related LBA Status Information log page, seeSTD-LOG-11.|

**4.4.1 Namespace Management/Attachment Commands**

The namespace management command along with the attach/detach commands is used to increase device
over-provisioning beyond the default minimum over-provisioning.

|Device Usable Capacity|Minimum Number of Namespaces|
|---|---|
|<= 1 TiB|16|
|> 1 TiB but <= 2 TiB|32|
|> 2 TiB but <= 3 TiB|48|
|> 3 TiB but <= 4 TiB|64|
|…|…|
|> 7 TiB|128|

|Requirement<br>ID|Description|
|---|---|
|NSM-1|The namespace management commands shall be supported on all namespaces.|
|NSM-2|When creating a namespace, the default “Formatted LBA Size” parameter (FLBAS = 0) in the<br>Identify Namespace Data Structure (byte 26) shall correspond to the default sector size set<br>at the factory.|
|NSM-3|The LBA Format 0 Support field shall correspond to the default sector size set at the factory<br>(seeDP-CFG-1).|
|NSM-4|<br>The device shall support a minimum of 16 Namespaces (seeSection 13 Device Profiles).|
|<br>NSM-5|<br>For some models (seeSection 13 Device Profiles), the minimum number of namespaces<br>shall be at least 128 Namespaces at 7 TiB based on 16 Namespaces per TB of usable<br>capacity. The number of Namespaces shall be based on the device usable capacity as<br>follows:<br>**Device Usable Capacity**<br>**Minimum Number of Namespaces**<br><= 1 TiB<br>16<br>> 1 TiB but <= 2 TiB<br>32<br>> 2 TiB but <= 3 TiB<br>48<br>> 3 TiB but <= 4 TiB<br>64<br>… <br>… <br>> 7 TiB<br>128|
|NSM-6|The device shall report at least one Namespace Granularity Descriptor in the Namespace<br>Granularity List.|
|NSM-7|The device shall support the TNVMCAP and UNVMCAP fields in the Identify Controller Data<br>Structure.|

<!-- page 13 -->
|Requirement<br>ID|Description|
|---|---|
|NSM-8|The device shall not support extended LBA formats (i.e., the Extended LBA Formats<br>Supported bit in the Controller Attributes register in the Identify Controller data structure<br>shall be cleared to ‘0’).|

**4.4.2 Namespace Utilization (NUSE)**

|Requirement ID|Description|
|---|---|
|NUSE-1|The NUSE shall be equal to the number of logical blocks currently allocated in the<br>namespace.  NUSE cannot be hardcoded to be equal to NCAP.  Here is an example for a<br>200 GB device:<br>1. After a Format NVM command User Data Erase (SES = 001b), NUSE would be zero.<br>And the usage data would reflect that: 0.00 GB.<br>2. After writing 1 GB worth of data, the usage data is expected to show the following:<br>1.00 GB.<br>3. After filling the device, the usage data is expected to show the following: 200.00 GB.<br>4. If the host issues a 10 GB deallocate command and the device completes deallocation<br>of the data, the usage data would show the following: 190.00 GB.<br> <br>Deallocation may occur in the background after completion of the deallocate command<br>with NUSE updated accordingly as deallocation occurs.|

**4.4.3 UUID for DSSD Specific Information**

A UUID has been defined for use in commands to ensure that the vendor specific Log Identifiers and
Feature Identifiers used in this specification access the functionality defined in this specification (i.e., do not
access other vendor specific functionality that may use the same vendor specific identifiers).

<!-- page 14 -->
|Requirement ID|Description|
|---|---|
|UUID-1|The UUID List (NVMe-AD-10) shall contain a UUID List Entry that contains the UUID value<br>C194D55BE0944794A21D29998F56BE6Fh in big endian format. The Identifier Association<br>field in that UUID List Entry shall be cleared to 00b.<br>For clarity:<br>**Byte**<br>**Address**<br>**Value**<br>48<br>C1h<br>49<br>94h<br>50<br>D5h<br>51<br>5Bh<br>52<br>E0h<br>53<br>94h<br>54<br>47h<br>55<br>94h<br>56<br>A2h<br>57<br>1Dh<br>58<br>29h<br>59<br>99h<br>60<br>8Fh<br>61<br>56h<br>62<br>BEh<br>63<br>6Fh|
|UUID-2|The Get Features and Set Features commands shall support UUID Index functionality.|
|UUID-3|A Get Features command or a Set Features command with:<br>• <br>the UUID Index of the UUID (UUID-1) in the UUID List (NVMe-AD-10) or a zero UUID<br>Index; and<br>• <br>a vendor-specific Feature Identifier that is used in this specification (seeSection 4.15<br>Set/Get Feature Requirements) shall access the vendor specific Feature defined in this<br>specification.|
|UUID-4|The Get Log Page command shall support UUID Index functionality.|
|UUID-5|A Get Log Page command with:<br>• <br>the UUID Index of the UUID (UUID-1) in the UUID List (NVMe-AD-10) or a zero UUID<br>Index; and<br>• <br>a vendor-specific Log Page Identifier that is defined in this specification (seeSection<br>4.8.4 DSSD Log Page Requirements) <br>shall access the specified vendor specific log page defined in this specification.|
|UUID-6|The vendor-specific events in the Persistent Event log page shall support UUID Index<br>functionality.|

|Byte<br>Address|Value|
|---|---|
|48|C1h|
|49|94h|
|50|D5h|
|51|5Bh|
|52|E0h|
|53|94h|
|54|47h|
|55|94h|
|56|A2h|
|57|1Dh|
|58|29h|
|59|99h|
|60|8Fh|
|61|56h|
|62|BEh|
|63|6Fh|

<!-- page 15 -->
### **4.5 NVMe I/O Command Set**

|DEAC|FUA|Behavior|
|---|---|---|
|0b|0b|The device shall follow the NVM Express NVM Command Set<br>Specification, seeNVMe-1.|
|0b|1b|The device shall follow the NVM Express NVM Command Set<br>Specification, seeNVMe-1.|
|1b|1b|The device shall follow the NVM Express NVM Command Set<br>Specification, seeNVMe-1.|
|1b|0b|SeeNVMe-IO-6.|

|Requirement ID|Description|
|---|---|
|NVMe-IO-1|The device shall support all mandatory NVMe I/O commands.|
|NVMe-IO-2|The device shall support the Dataset Management command. For additional information<br>seeTRIM-1.|
|NVMe-IO-3|<br>Since the device is power fail safe (e.g., has Power Loss Protection (PLP)) the performance<br>shall not be degraded by any of the following:<br>• <br>FUA – i.e., forced unit access shall not incur a performance penalty.<br>• <br>Flush Cache – i.e., flush cache shall have no effect as the PLP makes any cache non-<br>volatile.<br>• <br>Volatile Write Cache (Feature Identifier 06h) Set Features to disable write-cache. This<br>command shall fail as described in the NVM Express Base Specification as there is no<br>volatile write cache.|
|NVMe-IO-4|The device shall support the Write Zeroes command. The following bits of the Write<br>Zeroes command shall be supported:<br>• <br>Deallocate (DEAC) bit.<br>• <br>Force Unit Access (FUA) bit.|
|NVMe-IO-5|The Write Zeroes command shall have the following behavior:<br>**DEAC FUA**<br>**Behavior**<br>0b<br>0b<br>The device shall follow the NVM Express NVM Command Set<br>Specification, seeNVMe-1. <br>0b<br>1b<br>The device shall follow the NVM Express NVM Command Set<br>Specification, seeNVMe-1. <br>1b<br>1b<br>The device shall follow the NVM Express NVM Command Set<br>Specification, seeNVMe-1. <br>1b<br>0b<br>SeeNVMe-IO-6.|
|NVMe-IO-6|If the Write Zeroes DEAC bit is set to 1b and the FUA bit is cleared to 0b, the device shall<br>deallocate the specified LBAs and shall return all zeros for any subsequent read to the<br>specified LBAs until modified by a command (e.g., Write, Copy, etc.), regardless of the<br>behavior of the Dataset Management command.|
|NVMe-IO-7|With the DEAC bit set to 1b and the FUA bit cleared to 0b one or more Write Zeroes<br>command(s) shall be able to completely deallocate the entire device including updating<br>the FTL map in less than one minute.|
|NVMe-IO-8|The device shall support the Compare command.|
|NVMe-IO-9|The device shall support the Compare and Write fused command pair.|
|NVMe-IO-10|For some models (seeSection 13 Device Profiles), the device shall support the Write<br>Uncorrectable command.|
|NVMe-IO-11|The Write Uncorrectable command shall support marking LBAs uncorrectable at a single<br>LBA granularity regardless of the number of LBAs in the FTL indirection granularity.|
|NVMe-IO-12|The device shall not limit the number of LBAs that the host is able to specify in a Write<br>Uncorrectable command beyond the minimum and maximum allowed by the NVM Express<br>NVM Command Set Specification. The host shall be able to send a single LBA.|

<!-- page 16 -->
|Requirement ID|Description|
|---|---|
|NVMe-IO-13|There shall be no limit on the total media capacity that can be marked uncorrectable by<br>Write Uncorrectable commands.|
|NVMe-IO-14|Uncorrectable errors (e.g., read errors) that are a consequence of a prior Write<br>Uncorrectable command shall not be counted in the SMART / Health Information log page<br>(Log Identifier 02h) Media and Data Integrity Errors field.|

### **4.6 Optional NVMe Feature Support**

The device shall also support the following NVMe features:

|Requirement ID|Description|
|---|---|
|NVMe-OPT-1|Obsolete.  Duplicate ofSTD-LOG-7 andSTD-LOG-8.|
|<br>NVMe-OPT-2|<br>Timestamp (Feature Identifier 0Eh) shall be supported to align the devices internal logs.|
|NVMe-OPT-3|Obsolete.  SeeTEL-5.|
|<br>NVMe-OPT-4|<br>If a timestamp has been set via Set Features for the Timestamp feature (Feature Identifier<br>0Eh), then:<br>a) the device shall maintain the timestamp across all Controller Level Resets other<br>than NVM Subsystem Reset (i.e., if a timestamp has been set, then it is only<br>permissible to clear the Timestamp Origin field to 000b due to an NVM Subsystem<br>Reset and the device shall set the Timestamp Origin field to 001b for all Controller<br>Level Resets other than NVM Subsystem Reset); and<br>b) saving the timestamp across an NVM Subsystem Reset is optional.|
|NVMe-OPT-5|The device shall never set the Synch field bit to 1b in the Timestamp (Feature Identifier<br>0Eh).|
|NVMe-OPT-6|The device shall only generate a Telemetry Log Changed event on an error condition and<br>shall not generate a Telemetry Log Changed event for periodic logging.|
|NVMe-OPT-7|The device shall report its Indirection Unit (IU) size in the Namespace Preferred Write<br>Granularity (NPWG) field in the Identify Namespace data structure.|
|NVMe-OPT-8|The device shall support sending Telemetry Log Notices (i.e., bit 3 of the Log Page<br>Attributes field shall be set to 1b).|
|NVMe-OPT-9|The device shall support the Namespace Attribute Changed asynchronous event and the<br>associated Changed Namespace List log page (i.e., bit 8 of the Optional Asynchronous<br>Events Supported field in the Identify Controller data structure shall be set to 1b).  This<br>event shall only be reported for namespaces that are attached to a controller.|
|NVMe-OPT-10|The device shall support the Firmware Activation Notices event (i.e., bit 9 of the Optional<br>Asynchronous Events Supported field in the Identify Controller data structure shall be set<br>to 1b).|
|NVMe-OPT-11|Obsolete.  SeeNVMe-AD-24.|
|<br>NVMe-OPT-12|<br>The device shall be composed of a single NVM subsystem.|
|NVMe-OPT-13|The Timestamp feature (Feature Identifier 0Eh) shall not be saveable.|
|NVMe-OPT-14|The device shall ignore reserved bits/fields received in commands or register writes (i.e.,<br>the device shall not generate an error if reserved bits/fields are not cleared to 0h).|
|NVMe-OPT-15|The device shall report its Indirection Unit (IU) size in the Namespace Atomic Write Unit<br>Power Fail (NAWUPF) field in the Identify Namespace data structure.|
|NVMe-OPT-16|The device shall support the Copy command and Source Range Entries Descriptor Format<br>0.|

<!-- page 17 -->
### **4.7 Command Timeout**

|Requirement ID|Description|
|---|---|
|CTO-1|NVMe Admin commands and TCG commands shall take no more than 10 seconds from<br>submission to completion.  CTO-1 does not apply to the time taken by background<br>operations (e.g., Device Self-test and Sanitize commands).  CTO-1 does not apply to<br>Asynchronous Event Request commands.|
|CTO-2|The only exception to CTO-1 shall be the Format NVM Command for non-Cryptographic<br>Erase operations.  Format NVM Cryptographic Erase and the TCG methods Revert,<br>RevertSP and GenKey shall comply with CTO-1.|
|CTO-3|OnceTTR-2 is satisfied, an individual I/O command (QD1) shall take no more than 8<br>seconds from submission to completion.  Under full load the device shall not have more<br>than 7 I/Os take more than 2 seconds in one hour.|
|CTO-4|I/O command processing time shall not be a function of device capacity.|
|CTO-5|Device supplier shall disclose any I/O scenario that could violate the timeout requirements<br>in CTO-1 through CTO-4.|
|CTO-6|The device shall set MDTS, the attributes of the Number of Queues feature (Feature<br>Identifier 07h) and Maximum Queue Entries Supported such that CTO-3 cannot be<br>violated.|
|CTO-7|A Crypto Erase sanitize operation, and any background activity initiated by a TCG<br>command (e.g., as indicated by OutstandingData) shall complete within 10 seconds.|
|CTO-8|A Block Erase sanitize operation and Format NVM command performing a User Data Erase<br>shall complete within 10 seconds per TB of device capacity (e.g., Block Erase sanitize of a<br>4TB device shall complete within 40 seconds).|
|CTO-9|The device shall report the  greater of the Sanitize Crypto Erase, Format NVM<br>Cryptographic Erase, TCG Opal Revert, TCG Opal RevertSP, or TCG Opal GenKey time in the<br>Estimated Time for Crypto Erase field in the Sanitize Status log page.|
|CTO-10|The device shall not set the Estimated Time fields in the Sanitize Status log page to a value<br>of FFFFFFFFh for supported Sanitize operations.|
|CTO-11|Formats between LBAF values with the Secure Erase Settings field cleared to 000b (No<br>secure erase operation requested) or 2h (Cryptographic Erase) shall complete within 10<br>seconds.|

### **4.8 Log Page Requirements**

**4.8.1 Standard Log Page Requirements**

|Requirement<br>ID|Description|
|---|---|
|STD-LOG-1|The device shall support the Error Information (Log Identifier 01h) log page.|
|STD-LOG-2|The device shall support the SMART / Health Information (Log Identifier 02h) log page.|
|STD-LOG-3|Under no conditions shall the Percentage Used field in the SMART / Health Information<br>(Log Identifier 02h) log page decrease to a lower value than previously reported.|
|STD-LOG-4|The Percentage Used field in the SMART / Health Information (Log Identifier 02h) log page<br>shall be based on the average P/E cycle of the device. In addition, this field shall be based<br>on the actual P/E cycle count of the media and not on the Power on Hours (POH) of the<br>device.|

<!-- page 18 -->
|Type|Event|
|---|---|
|01h|SMART / Health Log Snapshot|
|02h|Firmware Commit|
|03h|Timestamp Change|
|04h|Power-on or Reset|
|05h|NVM Subsystem Hardware Error<br>The device shall not log PCIe Unsupported Request errors that are<br>Advisory Non-Fatal|
|06h|Change Namespace|
|07h|Format NVM Start|
|08h|Format NVM Completion|
|09h|Sanitize Start|
|0Ah|Sanitize Completion|
|0Ch|Telemetry Log Created|
|0Dh|Thermal Excursion|
|DEh|Vendor Specific<br>This specification defines vendor specific events to report TCG command<br>execution (seeSection 4.8.2 TCG Events for Persistent Event Log and<br>Section 4.8.3 TCG Activity Event Format).|

|Requirement<br>ID|Description|
|---|---|
|STD-LOG-5|The device shall support the Firmware Slot Information (Log Identifier 03h) log page.|
|STD-LOG-6|The device shall support the Commands Supported and Effects (Log Identifier 05h) log<br>page.|
|STD-LOG-7|The device shall support the Telemetry Host-Initiated (Log Identifier 07h) log page.|
|STD-LOG-8|The device shall support the Telemetry Controller-Initiated (Log Identifier 08h) log page.|
|STD-LOG-9|The device shall support the Persistent Event Log (Log Identifier 0Dh) log page.|
|STD-LOG-10|The device shall support the following Persistent Event Log types:<br>**Type**<br>**Event**<br>01h<br>SMART / Health Log Snapshot<br>02h<br>Firmware Commit<br>03h<br>Timestamp Change<br>04h<br>Power-on or Reset<br>05h<br>NVM Subsystem Hardware Error<br>The device shall not log PCIe Unsupported Request errors that are<br>Advisory Non-Fatal<br>06h<br>Change Namespace<br>07h<br>Format NVM Start<br>08h<br>Format NVM Completion<br>09h<br>Sanitize Start<br>0Ah<br>Sanitize Completion<br>0Ch<br>Telemetry Log Created<br>0Dh<br>Thermal Excursion<br>DEh<br>Vendor Specific<br>This specification defines vendor specific events to report TCG command<br>execution (seeSection 4.8.2 TCG Events for Persistent Event Log and<br>Section 4.8.3 TCG Activity Event Format).|
|STD-LOG-11|The device shall support the LBA Status Information (Log Identifier 0Eh) log page. The<br>device is not required to support the related Get LBA Status command (seeNVMe-AD-27).|

<!-- page 19 -->
|Behavior<br>Type|Saturating Counter1|Reset2 Persistent|Power Cycle/PERST#<br>Persistent|
|---|---|---|---|
|0|Reserved|Reserved|Reserved|
|1|No (Runtime Value)|No (Runtime Value)|No (Runtime Value)|
|2|No|Yes|Yes|
|3|Yes|Yes|No|
|4|Yes|Yes|Yes|
|5|Yes|No|No|
|6|No|Yes|No|
|15-7|Reserved|Reserved|Reserved|

|Requirement<br>ID|Description|
|---|---|
|STD-LOG-12|The following behavior types are used to define the functional boundary condition<br>behaviors for saturating or wrapping, under reset conditions and power cycles.<br>**Behavior**<br>**Type**<br>**Saturating Counter1 **<br>**Reset2 Persistent**<br>**Power Cycle/PERST#**<br>**Persistent**<br>0 <br>Reserved<br>1 <br>No (Runtime Value)<br>No (Runtime Value)<br>No (Runtime Value)<br>2 <br>No<br>Yes<br>Yes<br>3 <br>Yes<br>Yes<br>No<br>4 <br>Yes<br>Yes<br>Yes<br>5 <br>Yes<br>No<br>No<br>6 <br>No<br>Yes<br>No<br>15-7<br>Reserved<br>1See SLOG-2 saturating counters.<br>2All Resets (e.g., Controller, NSSR, FLR, PCIe hot reset, etc.).<br>For Behavior Types 1 the counter shall reset to zero on either a Reset or a Power<br>Cycle/PERST#. For Behavior Type 6 the counter shall reset to zero only on a Power<br>Cycle/PERST#.|
|STD-LOG-13|The device shall support the Device Self-test (Log Identifier 06h) log page.|
|STD-LOG-14|The device shall support the Command and Feature Lockdown (14h) log page.|
|STD-LOG-15|The device shall support the Physical Interface Receiver Eye Opening Measurement (Log<br>Identifier 19h) log page per TP4119a.|
|STD-LOG-16|In addition to any receiver margining data and image plots, the device shall store<br>information required to evaluate the signal integrity of the receiver such as equalization<br>values like continuous time linear equalization (CTLE), variable gain amplifier (VGA), boost,<br>and decision feedback equalization (DFE) settings in the Eye Data field of the Physical<br>Interface Receiver Eye Opening Measurement log page.|
|STD-LOG-17|The device shall support the Endurance Group Information (Log Identifier 09h) log page.<br>The device shall use a single Endurance Group for the entire device. The device is not<br>required to support the Endurance Group Event Aggregate (Log Identifier 0Fh) log page.|
|STD-LOG-18|The device shall not support the SMART / Health Information log page on a per namespace<br>basis (i.e., bit 0 of the Log Page Attributes field in the Identify Controller data structure shall<br>be cleared to 0b).|
|STD-LOG-19|The Persistent Event log page, Telemetry Host-Initiated log page, Telemetry Controller-<br>Initiated log page, and Error Information log page shall not contain user data, or the result<br>of any computation performed on user data.|
|STD-LOG-20|The Persistent Event log page events shall be ordered so that the more recent events are<br>reported earlier in the log than older events (i.e., the most recent event is Persistent Event<br>0), and the events deemed less important by the vendor (e.g., old events, informational<br>events, etc.) are removed first when the log is trimmed due to lack of space to store all<br>events).|

<!-- page 20 -->
|Requirement<br>ID|Description|
|---|---|
|STD-LOG-21|The persistent event log reporting context shall be held until released by the host or until at<br>least 5 minutes has elapsed since the last host access of the log unless the log fills and<br>reporting context has to be released in order to remove events (see STD-LOG-20).  New<br>events that occur while the context is established shall not be dropped.|
|STD-LOG-22|The maximum size of the Persistent Event log page reported in the Persistent Event Log Size<br>field in the Identify Controller data structure shall be 5 MiB or greater.|
|STD-LOG-23|The device shall not lose log page data for any reason, unless otherwise specified (e.g., see<br>STD-LOG-20 and the purge exception in this requirement).<br>Data that does not contain user data or data that could be used to derive user data<br>including the Telemetry Host-Initiated log page, Telemetry Controller-Initiated log page,<br>Persistent Event log page, Error Information log page, Vendor-specific log pages, SMART /<br>Health Information log page (Log Identifier 02h) including the Critical Warnings field,<br>SMART / Health Information Extended (Log Identifier C0h), and backup energy source<br>failure information shall be persisted across purge operations (seeSEC-43). <br>All log page data including the Telemetry Host-Initiated log page, Telemetry Controller-<br>Initiated log page, Persistent Event log page, Error Information log page, Vendor-specific log<br>pages, SMART / Health Information log page (Log Identifier 02h) including the Critical<br>Warnings field, SMART / Health Information Extended (Log Identifier C0h), and backup<br>energy source failure information shall be persisted across power loss, all resets, the<br>Format NVM command, and the device entering any protected mode (e.g., read only or<br>panic mode).<br>Issues with the device’s encryption engine shall not prevent access to the data specified by<br>this requirement.|

**4.8.2 TCG Activity Events for Persistent Event Log**

This defines the requirements for recording TCG Activity Events in the Persistent Event Log as Event Type
DEh (see STD-LOG-10).

|Requirement ID|Description|
|---|---|
|TCGHST-PE-1|The device shall support recording at least 100 TCG Activity Events in the Persistent Event<br>Log without deletion of any TCG Activity Events to make room for new events.|

<!-- page 21 -->
|Requirement ID|Description|
|---|---|
|TCGHST-PE-2|A TCG Activity Event entry shall be recorded in the Persistent Event Log whenever any of<br>the following TCG activities occurs (the event is recorded upon completion of the activity):<br>• <br>Level 0 Discovery<br>• <br>Start Session<br>• <br>Authenticate method (entries only recorded when the authority specified is not locked<br>out)<br>• <br>Close Session by the host when it sends an End-Of-Session token<br>• <br>Close Session due to timeout<br>• <br>Properties method<br>• <br>Stack Reset<br>• <br>TPer Reset<br>• <br>Get method<br>• <br>Set method<br>• <br>GenKey method<br>• <br>Random method<br>• <br>Activate method<br>• <br>Revert method<br>• <br>RevertSP method<br>• <br>Reactivate method<br>• <br>Erase method<br>• <br>Block SID Authentication<br>• <br>Assign method<br>• <br>Deassign method|
|TCGHST-PE-3|Redundant TCG activities shall not generate new TCG Command Event entries in the<br>Persistent Event Log. A TCG activity shall be considered redundant if it meets ALL the<br>following criteria with respect to a TCG Activity Event that is already recorded in the<br>Persistent Event Log:<br>• <br>Power cycle count is the same; and<br>• <br>Active firmware revision is the same; and<br>• <br>TCG activity is the same as the most recent TCG Activity Event entry; and<br>• <br>Tper state remains the same (i.e., there has been no change either in the device<br>behavior or host visible state); and<br>• <br>The Result field is the same.<br>The following are examples of TCG activities that do not generate a new TCG Activity Event<br>entry:<br>• <br>Setting an attribute of a TCG Object to a value that is the same as the current value.<br>• <br>Getting or setting the value of an informative attribute of a TCG object (e.g., the<br>CommonName of a Locking Object).<br>• <br>Getting data from or setting data to byte tables.<br>• <br>An unsuccessful authentication attempt that returns AUTHORITY_LOCKED_OUT status.|
|TCGHST-PE-4|TCG Activity Event entries shall not be removed for any TCG-specific reason (e.g., TCG<br>Revert/RevertSP or TCG Manufactured-Inactive), except as required to make room in the<br>Persistent Event Log for additional TCG Activity Event entries (seeTCGHST-PE-1).|

<!-- page 22 -->
|Requirement ID|Description|
|---|---|
|TCGHST-PE-5|TCG Activity Event format shall follow the requirements in the TCG Activity Event Format<br>section.|

**4.8.3 TCG Activity Event Format**

This defines the TCG Activity Event format for the Persistent Event Log when using Event Type DEh (see
STD-LOG-10 and [Section 4.8.2 TCG Activity Events for Persistent Event Log](bookmark://_TCG_Activity_Events/) ).

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCGCE-1|0|Event Type|1|Shall be set to DEh to indicate a vendor-specific event.|
|TCGCE-2|1|Event Type<br>Revision|1|Shall be set to 01h to indicate the revision in this<br>specification.|
|TCGCE-3|2|Event Header<br>Length (EHL)|1|Shall be set to 15h to indicate that 21 bytes of event<br>header information follow and the total event header<br>length (starting from byte 0) is 24 bytes.|
|TCGCE-4|3|Event Header<br>Additional<br>Information<br>(EHAI)|1|Bits 7:2 are reserved and shall be cleared to 0h.<br>Bits 1:0 shall be set to 01b if the event is associated<br>with an NVM subsystem port and shall be set to 10b if<br>the event is associated with a Management Endpoint.|
|TCGCE-5|5:4|Controller<br>Identifier|2|Shall contain the NVMe controller identifier for the<br>controller that is associated with the TCG activity.|
|TCGCE-6|13:06|Event<br>Timestamp|8|Shall indicate the Timestamp of when the TCG activity<br>was completed. This field contains an 8-byte data<br>structure whose format matches the data structure<br>returned by a Get Features command that specifies<br>the Timestamp feature (Feature Identifier 0Eh).|
|TCGCE-7|15:14|Port Identifier<br>(PELPID)|2|Shall contain a Port Identifier as specified in the<br>definition of this field in the NVM Express Base<br>Specification.|
|TCGCE-8|19:16|Reserved|4|Shall be cleared to zero.|
|TCGCE-9|21:20|Vendor Specific<br>Information<br>Length|2|Shall be set to 04h to align the start of the Vendor<br>Specific Event Data to an 8-byte multiple from the<br>start of this data structure.|
|TCGCE-10|23:22|Event Length|2|Shall be set to 30h to indicate that 48 bytes of vendor<br>specific information and vendor specific event data<br>follow the event header.|
|TCGCE-11|27:24|Vendor Specific<br>Information|4|Shall be cleared to zero for padding to align fields that<br>follow.|
|TCGCE-12|29:28|Vendor Specific<br>Event Code|2|Shall be set to 0001h.|
|TCGCE-13|30|Vendor Specific<br>Event Data Type|1|Shall be set to 3h to indicate Binary data.|
|TCGCE-14|31|UUID Index|1|Shall be set to the UUID Index of the UUID (UUID-1) in<br>the UUID List (NVMe-AD-10).|

<!-- page 23 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCGCE-15|33:32|Vendor Specific<br>Event Data<br>Length (VSEDL)|2|Shall be set to 26h to indicate that the length of the<br>vendor specific event data is 38 bytes.|
|TCGCE-16|35:34|Reserved|2|Shall be cleared to zero.|
|TCGCE-17|39:36|TCG Command<br>Count|4|Shall increment every time a TCG command is<br>completed regardless of the result and an entry is<br>recorded per TCGHST-PE-2 andTCGHST-PE-3.  This<br>value shall be cleared to zero when the device is<br>shipped from the factory.|
|TCGCE-18|47:40|Invoking ID|8|The 8-byte UID of the table, object, or SP associated<br>with the event (e.g., for a method, this indicates the<br>entity upon which the method is invoked).|
|TCGCE-19|55:48|Method ID|8|The 8-byte UID of the method being invoked.|
|TCGCE-20|57:56|ComID|2|The 2-byte ComID specified by the host in the<br>command.|
|TCGCE-21|58|ProtocolID|1|The Protocol Id specified by the host in the command.|
|TCGCE-22|59|Status|1|The TCG status on completion of the command.|
|TCGCE-23|61:60|Process Time|2|Time in milliseconds it took to process the<br>command.|
|TCGCE-24|71:62|TCG Activity<br>Specific Context|10|Additional context for a TCG activity. If an activity has<br>no additional context this field shall be cleared to 0h.<br>Any unused bytes shall be cleared to 0h.|

**4.8.3.1** **TCG Activity Specific Context**

This defines the additional command specific context for specific TCG activities (TCGCE-24).

**4.8.3.1.1** **Authenticate Method**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCG-AUTHM-<br>1|69:62|Authority<br>ID|8|The 8-byte UID of the authority on which the<br>authenticate method is being invoked.|
|TCG-AUTHM-<br>2|70|Tries<br>Count|1|The value of the Tries column of the C_PIN object<br>corresponding to the authority after the authenticate<br>method completes.|
|TCG-AUTHM-<br>3|71|Reserved|1|Shall be cleared to zero.|

**4.8.3.1.2** **Activate Method**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCG-ACT-1|62|Range Start<br>Range Length<br>Policy|1|The value of the RangeStartRangeLengthPolicy<br>parameter passed to the Activate method.|

<!-- page 24 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCG-ACT-2|71:63|Reserved|9|Shall be cleared to zero.|

**4.8.3.1.3** **Reactivate Method**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCG-RACT-1|62|Range Start<br>Range Length<br>Policy|1|The value of the RangeStartRangeLengthPolicy<br>parameter passed to the Reactivate method.|
|TCG-RACT-2|71:63|Reserved|9|Shall be cleared to zero.|

**4.8.3.1.4** **Assign Method**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCG-ASGN-1|65:62|Namespace<br>Id|4|The value of the NamespaceID parameter passed to<br>the Assign method.|
|TCG-ASGN-2|71:66|Reserved|6|Shall be cleared to zero.|

**4.8.3.1.5** **Block SID Authentication Command**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|TCG-BSID-1|62|Clear<br>Events|1|The value of the Clear Events parameter passed to the<br>Block SID Authentication command.|
|TCG-BSID-2|71:63|Reserved|9|Shall be cleared to zero.|

**4.8.4 DSSD Log Page Requirements**

The following table defines the scope for all DSSD specific log pages:

|Log Identifier|Scope|Log Page Name|Reference Section|
|---|---|---|---|
|C0h|Controller|SMART / Health Information Extended|4.8.6|
|C1h|NVM subsystem|Error Recovery|4.8.7|
|C2h|Obsolete|Obsolete|Obsolete|
|C3h|Controller|Latency Monitor|4.8.8|
|C4h|NVM subsystem|Device Capabilities|4.8.10|
|C5h|NVM subsystem|Unsupported Requirements|4.8.12|
|C6h|NVM subsystem|Hardware Component|4.8.13|
|C7h|NVM subsystem|TCG Configuration|4.8.14|
|C8h|Reserved for future use|Reserved for future use|Reserved for future use|
|C9h|NVM subsystem|Telemetry String|4.8.15|
|CAh|NVM subsystem|Latency Monitor Debug Telemetry|4.8.8|

<!-- page 25 -->
|Log Identifier|Scope|Log Page Name|Reference Section|
|---|---|---|---|
|KEY:<br>• <br>Namespace = The log page contains information about a specific namespace.<br>• <br>Controller = The log page contains information about the controller that is processing the<br>command.<br>• <br>NVM subsystem = The log page contains information about the NVM subsystem.|KEY:<br>• <br>Namespace = The log page contains information about a specific namespace.<br>• <br>Controller = The log page contains information about the controller that is processing the<br>command.<br>• <br>NVM subsystem = The log page contains information about the NVM subsystem.|KEY:<br>• <br>Namespace = The log page contains information about a specific namespace.<br>• <br>Controller = The log page contains information about the controller that is processing the<br>command.<br>• <br>NVM subsystem = The log page contains information about the NVM subsystem.|KEY:<br>• <br>Namespace = The log page contains information about a specific namespace.<br>• <br>Controller = The log page contains information about the controller that is processing the<br>command.<br>• <br>NVM subsystem = The log page contains information about the NVM subsystem.|

The following table defines the interactions for all DSSD specific log pages with the Format NVM command
and sanitize operations:

|Requirement ID|Description|
|---|---|
|GLP-ACC-1|The DSSD log pages to which access is allowed during a Format NVM command or sanitize<br>operations are listed below.  Note that this requirement requires vendor-specific log pages<br>to be accessible during Sanitize which overrides the requirement in the NVM Express Base<br>Specification to prohibit access to vendor-specific log pages during Sanitize.<br>**DSSD Log Pages**<br>SMART / Health Information Extended (C0h)<br>Error Recovery (C1h)<br>Device Capabilities (C4h)<br>Unsupported Requirements (C5h)<br>Hardware Component (C6h)<br>TCG Configuration (C7h)|

**4.8.5 SMART / Health Information Requirements**

The requirements for the SMART / Health Information log page (Log Identifier 02h) and SMART / Health
Information Extended log page (Log Identifier C0h) are in Section 4.8.1 Standard Log Page Requirements and the
following table:

|Requirement ID|Description|
|---|---|
|SLOG-1|All values in the DSSD log pages defined by this specification shall be persistent across<br>power cycles unless otherwise specified.|
|SLOG-2|All counters defined by this specification shall be saturating counters (i.e., if the counter<br>reaches the maximum allowable size, it stops incrementing and does NOT roll back to 0)<br>unless otherwise specified.|
|SLOG-3|All fields in DSSD log pages shall be little endian format.|
|SLOG-4|A normalized counter defined by this specification, unless otherwise specified, shall be<br>reported as the following: 100% shall represent the number at factory exit. 1% shall<br>represent the minimum amount for the device to be reliable. A value of 0% means the<br>device shall no longer be considered reliable. 100% shall be represented as 64h.|
|SLOG-5|The device shall support all fields in the SMART / Health Information log page.|

<!-- page 26 -->
|Requirement ID|Description|
|---|---|
|SLOG-6|A Get Log Page command for either the SMART /Health Information (Log Identifier 02h) or<br>SMART / Health Information Extended (Log Identifier C0h) shall not require an update of<br>the SMART values other than the temperature values inSLOG-8.  It shall be a simple read<br>of the current data and shall not block IO.|
|SLOG-7|Unless otherwise specified, the device shall update the values of the SMART /Health<br>Information log page (Log Identifier 02h) and SMART / Health Information Extended log<br>page (Log Identifier C0h) in the background at least once every ten minutes.|
|SLOG-8|The composite and raw temperature sensor values shall be updated when the SMART /<br>Health Information log page is accessed.|
|SLOG-9|All assert events and controller-initiated log captures shall have an associated vendor-<br>specific “Reason Identifier” that uniquely identifies the assert /controller condition.|
|SLOG-10|Obsolete (seeSTD-LOG-23).|
|<br>SLOG-11|<br>Obsolete (seeSTD-LOG-23).|
|<br>SLOG-12|<br>The device shall not set any bits in the Critical Warning field in the SMART / Health<br>Information log page solely due to the value in the Percentage Used field in the SMART/<br>Health Information log page.|

**4.8.6 SMART / Health Information Extended (Log Identifier C0h)**

This log page shall be 512 bytes with the following functional requirements and field format:

|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-1|15:0|Physical<br>Media Units<br>Written|16|Shall contain the number of bytes written to the<br>media; this value includes both user and metadata<br>written to the user and system areas.  It shall be<br>possible to use this attribute to calculate the Write<br>Amplification Factor (WAF).|
|SMART-2|31:16|Physical<br>Media Units<br>Read|16|Shall contain the number of bytes read from the<br>media from both the user and system areas.|
|SMART-3|39:32|Bad User<br>NAND Blocks|8|The Raw count specifies the number of user NAND<br>blocks that have been retired for any reason (e.g.,<br>program fails, erase fails or other events). The<br>Normalized value is the percentage of user spare<br>blocks still available. The normalized value shall be<br>set to 64h, and the Raw count shall be cleared to<br>zero on factory exit.<br>**Byte Address**<br>**Byte Description**<br>39:38<br>Normalized value<br>37:32<br>Raw count<br>It should be noted that there are 2 bytes for<br>normalized and 6 bytes for raw count. SeeSLOG-4 <br>definition above.|

26

|Byte Address|Byte Description|
|---|---|
|39:38|Normalized value|
|37:32|Raw count|

<!-- page 27 -->
|Byte Address|Byte Description|
|---|---|
|47:46|Normalized value|
|45:40|Raw count|

|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-4|47:40|Bad System<br>NAND Blocks|8|The Raw count specifies the number of system<br>NAND blocks that have been retired for any reason<br>(e.g., program fails, erase fails or other events). The<br>Normalized value is the percentage of system spare<br>blocks still available. The normalized value shall be<br>set to 64h, and the Raw count shall be cleared to<br>zero on factory exit. It should be noted that there<br>are 2 bytes for normalized and 6 bytes for raw<br>count. SeeSLOG-4 definition above.<br>**Byte Address**<br>**Byte Description**<br>47:46<br>Normalized value<br>45:40<br>Raw count<br>A value of FFFF_FFFF_FFFF_FFFFh indicates that the<br>Bad User NAND block count field above represents<br>all blocks on the device and Bad System NAND<br>block count field is invalid.|
|SMART-5|55:48|XOR<br>Recovery<br>Count|8|The total number of times XOR was invoked to<br>recover data in NAND. This shall cover all reads<br>from NAND. Data recovery may have succeeded or<br>failed. This shall be cleared to zero on factory exit.|
|SMART-6|63:56|Uncorrectabl<br>e Read Error<br>Count|8|Total count of NAND reads that were not<br>correctable by read retries, all levels of ECC, or XOR.<br>This shall be a count of the number of times data<br>recovery fails and an uncorrectable read error is<br>returned to the host.|
|SMART-7|71:64|Soft ECC<br>Error Count|8|Total count of NAND reads that were not<br>correctable by first level ECC and requires invoking<br>additional recovery. This shall cover all NAND read<br>accesses. Data recovery may have succeeded or<br>failed. If the device has more than one recovery<br>level, then this counter only increments once per<br>recovery action.|
|SMART-8|79:72|End to End<br>Correction<br>Counts|8|The Detected Error count is a count of the detected<br>errors by the end-to-end error protection<br>mechanisms which includes DRAM, SRAM, or other<br>storage element ECC/CRC protection mechanism<br>(not NAND ECC).  The Detected Error counter shall<br>increment on all detected end-to-end errors<br>regardless of if the error is corrected or<br>uncorrectable.<br>**Byte Address Byte Description**<br>79:76<br>Corrected Errors<br>75:72<br>Detected Errors|

27

|Byte Address|Byte Description|
|---|---|
|79:76|Corrected Errors|
|75:72|Detected Errors|

<!-- page 28 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-9|80|System<br>Data % Used|1|A normalized cumulative count of the number of<br>erase cycles per block since leaving the factory for<br>the system (firmware and metadata) area.  Starts at<br>0 and increments.  100 indicates that the estimated<br>endurance has been consumed.  Value may exceed<br>100 up to 255.  This count shall increment<br>regardless of what the backing media of the blocks<br>are (e.g., SLC and TLC).  If system data is split<br>between media types, then this shall report the<br>worst-case count so that the device wear out is<br>clearly understood.  This counter has a different<br>behavior than the normalized counter definition in<br>SLOG-4, 100% (64h) represents the device many no<br>longer function reliably as the max erase cycles has<br>been hit.|
|SMART-10|87:81|Refresh<br>Counts|7|This is a count of the number of blocks that have<br>been re-allocated to maintain data integrity.   This<br>counter does not include creating free space due to<br>garbage collection orblock reallocation due to wear<br>leveling.|
|SMART-11|95:88|User Data<br>Erase Counts|8|The maximum count and the minimum erase count<br>across the user NAND blocks in the device.  The<br>host shall not be able to reset this counter.  It<br>should be noted there are 4 bytes for the maximum<br>and 4 bytes for the minimum.  The Minimum User<br>Data Erase Count shall not include bad blocks.  If a<br>block goes bad, any subsequent attempts to<br>recover the block shall not increment the Maximum<br>User Data Erase Count field.<br>**Byte**<br>**Address**<br>**Byte Description**<br>95:92<br>Minimum User Data<br>Erase Count<br>91:88<br>Maximum User Data<br>Erase Count|

|Byte<br>Address|Byte Description|
|---|---|
|95:92|Minimum User Data<br>Erase Count|
|91:88|Maximum User Data<br>Erase Count|

<!-- page 29 -->
|Byte<br>Address|Byte Description|
|---|---|
|97|Current Throttling Status:<br>• <br>00h = unthrottled<br>• <br>01h = first level throttle<br>• <br>02h = 2nd level throttle<br>• <br>03h = 3rd level throttle<br>• <br>04h – FFh = Reserved|
|96|Number of thermal throttling<br>events|

|Byte<br>Address|Byte Description|
|---|---|
|103|Major Version Field.<br>Shall be 02h.|
|102:101|Minor Version Field.<br>Shall be 0005h.|
|100:99|Point Version Field.  Shall<br>be 0000h.|
|98|Errata Version Field.<br>Shall be 00h.|

|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-12|97:96|Thermal<br>Throttling<br>Status and<br>Count|2|The current status of thermal throttling (throttled<br>or not throttled) and a count of the number of<br>thermal throttling initiation events independent of<br>level.  Note that there is 1 byte for the current<br>status and 1 byte for the count. This shall be<br>cleared to zero on factory exit.<br>**Byte**<br>**Address**<br>**Byte Description**<br>97<br>Current Throttling Status:<br>• <br>00h = unthrottled<br>• <br>01h = first level throttle<br>• <br>02h = 2nd level throttle<br>• <br>03h = 3rd level throttle<br>• <br>04h – FFh = Reserved<br>96<br>Number of thermal throttling<br>events|
|SMART-13|103:98|DSSD<br>Specification<br>Version|6|Version of the DSSD Specification that this device<br>conforms to.<br>**Byte**<br>**Address**<br>**Byte Description**<br>103<br>Major Version Field.<br>Shall be 02h.<br>102:101<br>Minor Version Field.<br>Shall be 0005h.<br>100:99<br>Point Version Field. Shall<br>be 0000h.<br>98<br>Errata Version Field.<br>Shall be 00h.|
|SMART-14|111:104|PCIe<br>Correctable<br>Error Count|8|Summation counter of all PCIe correctable errors<br>(bad TLP, bad DLLP, receiver error, replay timeouts,<br>replay rollovers). These counts shall only increment<br>during run time. They shall not increment during<br>training or power fail. This shall be cleared to zero<br>on factory exit.|
|SMART-15|115:112|Incomplete<br>Shutdowns|4|A count of the number of shutdowns that have<br>occurred that did not completely flush all required<br>user data and metadata to non-volatile memory for<br>any reason. This shall be cleared to zero on factory<br>exit.|
|SMART-16|119:116|Reserved|4|Shall be cleared to zero.|

<!-- page 30 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-17|120|% Free<br>Blocks|1|This field is the normalized counter of the number<br>of NAND blocks which are currently erased and<br>ready to be written with user data, out of the total<br>number of NAND blocks in the spare area. i.e., this<br>is the percentage of erased NAND blocks in spare<br>area, where the spare area is defined as the NAND<br>blocks that contain no valid user data, no valid<br>system data, and are:<br>• <br>waiting to be erased for use to write user data;<br>or<br>• <br>already erased and ready to be used to write<br>user data.<br>i.e., % Free Blocks = A / (A + B) where A is the<br>number of currently erased NAND blocks and B is<br>the number of NAND blocks waiting to be erased.|
|SMART-18|127:121|Reserved|7|Shall be cleared to zero.|
|SMART-19|129:128|Capacitor<br>Health|2|This field is an indicator of the capacitor health and<br>represents the capacitor holdup energy margin<br>during operation. If no PLP protection is present a<br>value of FFFFh shall be reported. 100% represents<br>the passing hold up energy threshold when a device<br>leaves manufacturing. Thus, a device will typically<br>report greater than 100% in this field after leaving<br>manufacturing at the beginning of life. 1% is the<br>minimum hold up energy required to conduct a<br>proper shutdown reliably. A value of 0% may or<br>may not result in a device failing to shutdown<br>properly. This value shall never go negative. Zero is<br>the minimum.|

<!-- page 31 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-20|130|NVM Express<br>Base Errata<br>Version|1|The device shall report the most recent NVM<br>Express Base Specification Errata revision (a, b, c,<br>etc.) in ASCII that the device has implemented<br>backwards incompatible changes from. If the<br>device does not implement any backwards<br>incompatible changes due to errata, then this field<br>shall be cleared to 0h.|
|SMART-32|131|NVM<br>Command<br>Set Errata<br>Version|1|The device shall report the most recent NVM<br>Express NVM Command Set Specification errata<br>revision (a, b, c, etc.) in ASCII that the device has<br>implemented backwards incompatible changes<br>from. If the device does not implement any<br>backwards incompatible changes due to errata,<br>then this field shall be cleared to 0h.|
|SMART-34|132|NVMe over<br>PCIe<br>Transport<br>Errata<br>Version|1|The device shall report the most recent NVM<br>Express NVMe over PCIe Transport Specification<br>errata revision (a, b, c, etc.) in ASCII that the device<br>has implemented backwards incompatible changes<br>from. If the device does not implement any<br>backwards incompatible changes due to errata,<br>then this field shall be cleared to 0h.|
|SMART-35|133|NVM Express<br>Management<br>Interface<br>Errata<br>Version|1|The device shall report the most recent NVM<br>Express Management Interface Specification errata<br>revision (a, b, c, etc.) in ASCII that the device has<br>implemented backwards incompatible changes<br>from. If the device does not implement any<br>backwards incompatible changes due to errata,<br>then this field shall be cleared to zero.|
|SMART-30|135:134|Reserved|2|Shall be cleared to zero.|
|SMART-21|143:136|Unaligned<br>I/O|8|This is a count of the number of write IOs<br>performed by the device that are not aligned to the<br>indirection unit size (IU) of the device. Alignment<br>indicates only the start of each IO. The length does<br>not affect this count. This counter shall reset on<br>power cycle. This counter shall not wrap. This shall<br>be cleared to zero on factory exit.|
|SMART-22|151:144|Security<br>Version<br>Number|8|This is the Security Version Number of the currently<br>running firmware image. The value of this field<br>shall be 0h for the initial release of firmware. The<br>supplier shall increment this field by one any time a<br>firmware includes a fix for a security issue or critical<br>firmware fix that customer agrees rollback<br>prevention is required.|

<!-- page 32 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-23|159:152|Total NUSE|8|Total Namespace Utilization. For a device with a<br>single Namespace, this shall be a copy of the<br>Namespace Utilization field defined in the Identify<br>Namespace Data Structure bytes 23:16. For a<br>device with multiple Namespaces, this shall reflect<br>the total utilization based on all the Namespaces.|
|SMART-24|175:160|PLP Start<br>Count|16|This is a count of the number of times the device<br>has initiated its power loss protection process due<br>to supply voltage drop. This counter shall be<br>incremented on the initial detection of the power<br>loss condition. This does not include PLP health<br>check operations.|
|SMART-25|191:176|Endurance<br>Estimate|16|This field is an estimate of the total number of data<br>bytes that may be written to the device over its<br>lifetime assuming a write amplification of 1 (i.e., no<br>increase in the number of write operations<br>performed by the device beyond the number of<br>write operations requested by a host). This value<br>shall be equivalent to the Endurance Estimate field<br>in the Endurance Group log page (Log Identifier<br>09h) but shall be in units of bytes.|
|SMART-29|199:192|PCIe Link<br>Retraining<br>Count|8|This is a count of the number of PCIe Link<br>Retraining events (including link speed and link<br>width changes). This count shall only increment<br>during runtime. It shall not increment during<br>training due to resets or power cycles. This shall be<br>cleared to zero on factory exit.|
|SMART-31|207:200|Power State<br>Change<br>Count|8|Summation counter of the number of NVMe Power<br>State changes whether host or device initiated,<br>including NVMe Power State changes caused by<br>DSSD Power State changes (seeSection 4.8.11 DSSD<br>Power State Requirements). This count shall only<br>increment during run time. This shall be cleared to<br>zero on factory exit.|

<!-- page 33 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-33|215:208|Lowest<br>Permitted<br>Firmware<br>Revision|8|This field indicates the value of the Firmware<br>Revision field of the lowest firmware revision that is<br>permitted to be rolled back to.<br>If the currently active firmware image permits<br>rollback to all prior firmware revision, then this field<br>shall be cleared to 0h.<br>If the currently active firmware image does not<br>permit rollback to all prior firmware revisions, then<br>this field shall indicate the value of the Firmware<br>Revision field of the lowest firmware revision that<br>has a Firmware Security Version equal to the<br>Firmware Security Version of the currently active<br>firmware image.|
|SMART-36|217:216|Total Media<br>Dies|2|This field is the total number of media dies in the<br>device.|
|SMART-37|219:218|Media Die<br>Failure<br>Tolerance|2|This field is the number of flash dies that are<br>allowed to fail and the device will continue to<br>operate.|
|SMART-38|221:220|Media Dies<br>Offline|2|This is a count of the number of media dies<br>permanently offline (retired).|
|SMART-39|222|Max<br>Temperature<br>Recorded|1|This value shall report the highest composite<br>temperature value recorded over the life of the<br>device in degrees Celsius.|
|SMART-40|223|Reserved|1|Shall be cleared to 0h.|
|SMART-41|231:224|NAND Avg.<br>Erase Count|8|Average erase count of all flash blocks across entire<br>device.|
|SMART-42|235:232|Command<br>Timeouts|4|This is a count of the number of times a command<br>with the limited retry (LR) bit set has exceeded the<br>TLER value. This is a saturating count.|
|SMART-43|243:236|System Area<br>Program Fail<br>Count|8|The Raw count specifies the number of program<br>failures in the system area. The Normalized value is<br>the percentage of remaining allowable failures. The<br>first four bytes shall be the raw value, the fifth byte<br>the normalized value, and the last 3 bytes are<br>reserved.<br> <br>**Byte Address**<br>**Byte Description**<br>241:239<br>Reserved<br>238<br>Normalized value<br>237:234<br>Raw count|

33

|Byte Address|Byte Description|
|---|---|
|241:239|Reserved|
|238|Normalized value|
|237:234|Raw count|

<!-- page 34 -->
|Byte Address|Byte Description|
|---|---|
|249:247|Reserved|
|246|Normalized value|
|245:242|Raw count|

|Byte Address|Byte Description|
|---|---|
|257:255|Reserved|
|254|Normalized value|
|253:250|Raw count|

|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-44|251:244|System Area<br>Uncorrectabl<br>e Read Count|8|The Raw count specifies the number of read failures<br>(Uncorrectable Reads) in the system area. The<br>Normalized value is the percentage of remaining<br>allowable failures. The first four bytes shall be the<br>raw value, the fifth byte the normalized value, and<br>the last 3 bytes are reserved.<br> <br>**Byte Address**<br>**Byte Description**<br>249:247<br>Reserved<br>246<br>Normalized value<br>245:242<br>Raw count|
|SMART-45|259:252|System Area<br>Erase Fail<br>Count|8|The Raw count specifies the number of erase<br>failures in the system area. The Normalized value is<br>the percentage of remaining allowable failures. The<br>first four bytes shall be the raw value, the fifth byte<br>the normalized value, and the last 3 bytes are<br>reserved.<br> <br>**Byte Address**<br>**Byte Description**<br>257:255<br>Reserved<br>254<br>Normalized value<br>253:250<br>Raw count|
|SMART-46|261:260|Max Peak<br>Power<br>Capability|2|The maximum peak power that the device is<br>capable of measured in Watts over a 100 uS<br>window with a sampling interval of 4 uS or smaller<br>(see PCM-2). This is a static value based on the PS0<br>worst case.|
|SMART-47|263:262|Current Max<br>Average<br>Power|2|The current device Max Average Power in Watts<br>measured over a 1 second window with a sampling<br>rate of 2 ms or smaller (seePCM-1).|
|SMART-48|269:264|Lifetime<br>Power<br>Consumed|6|The total cumulative power consumed by the<br>device in kWh based on the Current Max Average<br>Power. This field shall be cleared to 0h from the<br>factory. This is a saturating counter.|

<!-- page 35 -->

<!-- page 36 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|||||Pre-production firmware shall have a <Major<br>Revision> of “0”.  The first production release of<br>firmware shall have a <Major Revision> of “1”.  The<br><Major Revision> shall be incremented by one<br>whenever a major change is made to the firmware.<br>Examples of major changes include:<br>• <br>the Security Firmware Revision is<br>incremented;<br>• <br>major feature enhancements;<br>• <br>major architectural changes to the<br>firmware code base; and<br>• <br>addition of support for major hardware<br>changes.<br> <br>The first production release of firmware shall have<br>a <Minor Revision> of “0”.  The <Minor Revision><br>shall be incremented by one when only a minor<br>change is made to the firmware.  Examples of minor<br>changes include:<br>• <br>minor feature enhancements;<br>• <br>performance enhancements; and<br>• <br>multiple bug fixes that, in aggregate, justify<br>more than an increment to the <Release<br>Revision>.<br> <br>The <Release Revision> shall be incremented by<br>one for each firmware revision.|
|SMART-50|293:278|DSSD<br>Firmware<br>Build UUID|16|This field shall contain a UUID in the format<br>specified for UUIDs by the NVM Express Base<br>Specification that is unique for each firmware build.|
|SMART-51|357:294|DSSD<br>Firmware<br>Build Label|64|This field may contain a descriptive label for the<br>firmware that provides additional information<br>about the purpose of this revision of the firmware.<br>For example, this field may be used for test or<br>debug builds to describe the scope of the build.<br>• <br>Examples:<br>`o` Workaround for issue 12345<br>`o` Experimental new feature XYZ<br> <br>If a descriptive label is provided, then the label shall<br>adhere to the rules for ASCII strings as defined by<br>the NVM Express Base Specification; otherwise, this<br>field shall be cleared to 0h.|
|SMART-26|493:358|Reserved|136|Shall be cleared to zero.|

<!-- page 37 -->
|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|SMART-27|495:494|Log Page<br>Version|2|This indicates the version of the mapping this log<br>page uses.  Shall be set to 0005h.|
|<br>SMART-28<br>|511:496|Log Page<br>GUID<br>|16|Shall be set to<br>AFD514C97C6F4F9CA4F2BFEA2810AFC5h.|

**4.8.7 Error Recovery (Log Identifier C1h)**

The requirements for the Error Recovery (Log Identifier C1h) log page are in the following table:

|Requirement ID|Description|
|---|---|
|EREC-AEN-1|If the device uses Panic AEN to report a panic condition and the device encounters a panic<br>condition, then the device shall complete an outstanding Asynchronous Event Request<br>(AER) command with an Asynchronous Event Notification (AEN) with Completion Queue<br>Entry Dword 0 set as follows:<br>• <br>The Log Page Identifier field shall be set to C1h.<br>• <br>The Asynchronous Event Information field shall be set to 01h.<br>• <br>The Asynchronous Event Type field shall be set to 111b (Vendor Specific).|

**4.8.7.1** **Error Recovery Theory of Operations**

Error Recovery Workflow using Asynchronous Event Notifications.

|Requirement ID|Description|
|---|---|
|EREC-FUNC-1|The device shall make every attempt to transparently recover from errors and panics<br>without invoking any of the Error Recovery workflows described in the following tables.|

Panic Workflow – AEN with in-band recovery

|#|Task|Description|
|---|---|---|
|**Pre-Failure Parameter Exchange**|**Pre-Failure Parameter Exchange**|**Pre-Failure Parameter Exchange**|
|1|Boot time controller<br>initialization|During boot time controller initialization, the host reads the Error Recovery<br>(Log Identifier C1h) and caches the Panic Reset Wait Time and the Panic Reset<br>Action bitfield. The host also sends an Asynchronous Event Request (AER)<br>command to device and waits for the device to complete the command when<br>there is an asynchronous event.|
|**Re-Establishing Communication When Failure Occurs**|**Re-Establishing Communication When Failure Occurs**|**Re-Establishing Communication When Failure Occurs**|
|2|Device hits panic<br>condition|The device detects panic condition|
|3|Device saves panic<br>related data|The device saves the following information:<br>• <br>Panic ID<br>• <br>Device Recovery Actions<br>• <br>Debug data for the Telemetry Controller-Initiated log page (Log Identifier<br>08h)|

<!-- page 38 -->
|#|Task|Description|
|---|---|---|
|4|Device generates AEN|The device generates AEN to let the host know that a panic was detected it<br>then starts its panic handling workflow. The device is not required to handle<br>any NVMe command(s) sent via the Admin Submission Queue after sending<br>the AEN. It is strongly recommended that the device continues to service<br>commands sent via the out-of-band mechanism, if possible.<br> <br>The AEN Completion Queue Entry Dword 0 is filled in perEREC-AEN-1.|
|5|Host AEN handling|The host services the AEN and logs an event for the panic condition.|
|6|Host waits for device<br>panic handling to<br>complete|The host waits for Panic Reset Wait Time to allow the device to finish its panic<br>handling workflow.|
|**Extracting Debug Information After Failure and Recovery**|**Extracting Debug Information After Failure and Recovery**|**Extracting Debug Information After Failure and Recovery**|
|7|Host recovers device|The host tries one or more of the resets specified in the Panic Reset Action<br>bitfield to attempt to bring the device back to a state where it can service<br>NVMe commands.|
|8|Host initiates controller<br>initialization|The host starts controller initialization. If the controller fails to initialize, the<br>host will attempt the next Panic Reset Action as specified in the Panic Reset<br>Action bitfield.|
|9|Host reads the Error<br>Recovery log page (Log<br>Identifier C1h)|The host reads the Error Recovery log page (Log Identifier C1h) to retrieve the<br>following information:<br>• <br>Last Panic ID<br>• <br>Device Recovery Actions<br>If the device is still in panic mode the device fails I/O commands if it cannot<br>safely complete commands:<br>• <br>Status Code (SC) = 06h (Internal Error)<br>• <br>Status Code Type (SCT) = 00h (Generic Command Status)|
|10|Host retrieves<br>Controller-Initiated<br>Telemetry Log if device<br>in panic mode|Host retrieves Telemetry Controller-Initiated log page (Log Identifier 08h) for<br>later use in debugging.|
|11|Device Recovery|The recommended Device Recovery Actions are taken. This is done during<br>the offline recovery workflow.|

Panic Workflow – CFS with in-band recovery

|#|Task|Description|
|---|---|---|
|**Pre-Failure Parameter Exchange**|**Pre-Failure Parameter Exchange**|**Pre-Failure Parameter Exchange**|
|1|Boot time controller initialization|During boot time controller<br>initialization, driver reads the Error<br>Recovery log page (Log Identifier<br>C1h) and caches Panic Reset Wait<br>Time and Panic Reset Action.|

<!-- page 39 -->
|#|Task|Description|
|---|---|---|
|||Driver also saves information that<br>Panic CFS Supported is set.|
|**Re-Establishing Communication When Failure Occurs**|**Re-Establishing Communication When Failure Occurs**|**Re-Establishing Communication When Failure Occurs**|
|2|Device hits panic condition|Device detects panic condition|
|3|Device saves panic related data|Device saves the following<br>information:<br>• <br>Panic ID<br>• <br>Device Recovery Actions<br>• <br>Debug data for the Telemetry<br>Controller-Initiated log page<br>(Log Identifier 08h)|
|4|Device asserts CFS|Device asserts CFS to let host know<br>that a panic was detected and<br>starts panic handling workflow.<br>Device is not expected to be able to<br>handle any NVMe command(s)<br>sent via the Admin Submission<br>Queue after asserting CFS. It is<br>strongly recommended that the<br>device continues to service<br>commands sent via the out-of-<br>band mechanism, if possible.|
|5|Driver detects CFS after command<br>timeout|On first command timeout after<br>CFS bit is set, driver will check and<br>detect CFS bit is set.|
|6|Driver waits for device panic<br>handling to complete|The driver waits for Panic Reset<br>Wait Time to allow the device to<br>finish its panic handling workflow.|
|**Extracting Debug Information After Failure and Recovery**|**Extracting Debug Information After Failure and Recovery**|**Extracting Debug Information After Failure and Recovery**|
|7|Driver initiates a NVMe Controller<br>Reset|The driver initiates an NVMe<br>Controller Reset as recommended<br>in the NVM Express Base<br>Specification for CFS.|
|8|Driver resets device if NVMe<br>Controller Reset fails|If prior NVMe Controller Reset fails,<br>driver tries one or more resets<br>specified in Panic Reset Action to<br>attempt to bring device back to a<br>state that can service NVMe<br>command(s).|
|9|Driver initiates controller<br>initialization|Driver starts controller<br>initialization. If controller fails to|

<!-- page 40 -->
|#|Task|Description|
|---|---|---|
|||initialize, driver may attempt a<br>different Panic Reset Action.|
|10|Driver reads the Error Recovery log<br>page (Log Identifier C1h)|Driver reads the Error Recovery log<br>page (Log Identifier C1h) to retrieve<br>the following information:<br>• <br>Last Panic ID<br>• <br>Device Recovery Actions<br>If the device is still in panic mode<br>the device fails I/O commands if it<br>cannot safely complete commands:<br>● <br>Status Code (SC) = 06h<br>(Internal Error)<br>● <br>Status Code Type (SCT) = 0h<br>(Generic Command Status)|
|11|Driver retrieves the Telemetry<br>Controller-Initiated log page (Log<br>Identifier 08h) if device in panic<br>mode|Driver retrieves the Telemetry<br>Controller-Initiated log page (Log<br>Identifier 08h) for sharing with IHV.|
|12|Device Recovery|The recommended Device<br>Recovery Actions are taken. This is<br>done during the offline recovery<br>workflow.|

This vendor-specific log page, C1h shall be 512 bytes with the following functional requirements and field
format:

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EREC-1|1:0|Panic Reset<br>Wait Time|2|The amount of time the host should wait for the device<br>panic workflow to complete in msec.|

<!-- page 41 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EREC-2|2|Panic Reset<br>Action|1|Bit field indicating potential reset actions that may need to<br>be taken. If no reset action is needed, do not set any of the<br>bits. More than 1 bit can be set, and it is up to the host to<br>decide the sequence of action(s) to take.<br>Instead of asserting and requiring the host to perform an<br>NVMe Controller Reset to clear the assert condition, the<br>device should reset itself using a methodology similar to<br>what is used to perform a firmware activation without<br>reset (e.g., pause command processing, set the Processing<br>Paused bit to 1b, save runtime state, re-initialize firmware,<br>restore runtime state, resuming processing, clear the<br>Processing Paused bit to 0b). The device shall increment<br>the Panic Count field (see EREC-16) and shall log this event<br>in the telemetry logs and include a vendor specific panic<br>code in the Error ID (seeTELRI-1) whether or not it can<br>autonomously recover.<br>If autonomous recovery is not possible, then the assert<br>condition shall be reported to the host (seeEREC-5).<br>The strongly preferred order of device advertised recovery<br>is bit 0, 1, 2, 5, 3 then 4 which is based on least impactful to<br>most impactful from a host perspective.<br>**Bit**<br>**Bit Description**<br>7:6 Reserved. Shall be cleared to zero.<br>5 <br>PCIe Conventional Hot Reset.<br>4 <br>Main Power Cycle.<br>3 <br>PERST#.<br>2 <br>PCIe Function Level Reset.<br>1 <br>NVM Subsystem Reset.<br>0 <br>NVMe Controller Reset.|

41

|Bit|Bit Description|
|---|---|
|7:6|Reserved.  Shall be cleared to zero.|
|5|PCIe Conventional Hot Reset.|
|4|Main Power Cycle.|
|3|PERST#.|
|2|PCIe Function Level Reset.|
|1|NVM Subsystem Reset.|
|0|NVMe Controller Reset.|

<!-- page 42 -->
|Bit|Bit Description|
|---|---|
|7|Reserved.  Shall be cleared to zero.|
|6|Device panic has caused user data loss.  The device<br>shall populate LBA Status Information log page (Log<br>Identifier 0Eh) with all of the lost/corrupted LBAs.<br>If the device sets this bit to 1b, then the device shall<br>also set at least one bit to 1b in Device Recovery<br>Action 2, see EREC-14.|
|5|Sanitize Required.|
|4|Device Replacement Required.|
|3|Vendor Physical Analysis Required.|
|2|Vendor Specific Command Required.|
|1|Format NVM Required (Any SES value, any<br>supported combination of other parameters – PIL,<br>PI, MSET, LBAF).|
|0|No Action Required.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EREC-3|3|Device<br>Recovery<br>Action 1|1|The recovery action to take for handling a device panic<br>condition. Value is dependent on the panic condition. The<br>device shall set bit 0 to 1b if data integrity is intact. The<br>device shall set bit 6 to 1b if the data integrity of some of<br>the LBAs is compromised. The device shall only set bit 1,<br>bit 2 or bit 5 to 1b if the data integrity of all of the LBAs is<br>compromised. The device shall only set bit 3 to 1b or bit 4<br>to 1b if there is a persistent hardware failure. The device<br>shall not set more than one bit to one in this field.<br>**Bit**<br>**Bit Description**<br>7 <br>Reserved. Shall be cleared to zero.<br>6 <br>Device panic has caused user data loss. The device<br>shall populate LBA Status Information log page (Log<br>Identifier 0Eh) with all of the lost/corrupted LBAs.<br>If the device sets this bit to 1b, then the device shall<br>also set at least one bit to 1b in Device Recovery<br>Action 2, see EREC-14.<br>5 <br>Sanitize Required.<br>4 <br>Device Replacement Required.<br>3 <br>Vendor Physical Analysis Required.<br>2 <br>Vendor Specific Command Required.<br>1 <br>Format NVM Required (Any SES value, any<br>supported combination of other parameters – PIL,<br>PI, MSET, LBAF).<br>0 <br>No Action Required.|
|EREC-4|11:4|Panic ID|8|A numeric value that uniquely identifies the exact panic<br>condition encountered. A value of zero indicates no panic.<br>The following Panic ID values are reserved for Host defined<br>fault codes for known panic conditions:<br>• <br>00000000_00000000h – 00000000_0000FFFFh<br>**Byte**<br>**Byte Description**<br>11:4<br>Panic ID definition:<br>• <br>00000000_00000001h – Panic caused by flush<br>failures or data loss during power loss<br>handling.|

|Byte|Byte Description|
|---|---|
|11:4|Panic ID definition:<br>• <br>00000000_00000001h – Panic caused by flush<br>failures or data loss during power loss<br>handling.|

<!-- page 43 -->
|Bit|Bit Description|
|---|---|
|31:2|Reserved.  Shall be cleared to zero.|
|1|Panic CFS Supported: If set, indicates device<br>supports using CFS to notify host of a panic<br>condition*.|
|0|Panic AEN Supported: If set, indicates device<br>supports using AEN to notify host of a panic<br>condition*.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EREC-5|15:12|Device<br>Capabilities|4|Field to indicate device capabilities.<br>**Bit**<br>**Bit Description**<br>31:2 Reserved. Shall be cleared to zero.<br>1 <br>Panic CFS Supported: If set, indicates device<br>supports using CFS to notify host of a panic<br>condition*.<br>0 <br>Panic AEN Supported: If set, indicates device<br>supports using AEN to notify host of a panic<br>condition*.<br>*Note: It is valid for a device to indicate support for both<br>Panic AEN Supported and Panic Controller Fatal Status<br>Supported. If the device supports both, the device shall<br>only use one of these in-band panic notification<br>mechanisms when reporting a given panic event as<br>configured in the DSSD Asynchronous Event Configuration<br>Feature (seeSDAEC-14).|
|EREC-6|16|Vendor<br>Specific<br>Recovery<br>Opcode|1|Vendor-specific command opcode to recover device from<br>panic condition. Only valid when bit 2 of the Device<br>Recovery Action 1 field value is set to 1b. When bit 2 of the<br>Device Recovery Action 1 field value is cleared to 0b, this<br>field shall be cleared to zero.|
|EREC-7|19:17|Reserved|3|Shall be cleared to zero.|
|EREC-8|23:20|Vendor<br>Specific<br>Command<br>CDW12|4|CDW12 value for the Vendor Specific command to recover<br>device from panic condition. Only valid when bit 2 of the<br>Device Recovery Action 1 field is set to 1b. When bit 2 of<br>the Device Recovery Action 1 field value is cleared to 0b,<br>this field shall be cleared to zero.|
|EREC-9|27:24|Vendor<br>Specific<br>Command<br>CDW13|4|CDW13 value for the Vendor Specific command to recover<br>device from panic condition. Only valid when bit 2 of the<br>Device Recovery Action 1 field value is set to 1b. When<br>Device Recovery Action 1 field value is cleared to 0b, this<br>field shall be cleared to zero.|
|EREC-13|28|Vendor<br>Specific<br>Command<br>Timeout|1|The amount of time the host should wait for the device to<br>complete the recovery command in seconds.|

<!-- page 44 -->
|Bit|Bit Description|
|---|---|
|7:6|Reserved.  Shall be cleared to zero.|
|5|PCIe Conventional Hot Reset.|
|4|Main Power Cycle.|
|3|PERST#.|
|2|PCIe Function Level Reset.|
|1|NVM Subsystem Reset.|
|0|NVMe Controller Reset.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EREC-14|29|Device<br>Recovery<br>Action 2|1|Bit field indicating potential post reset actions that may<br>need to be taken. If no reset action is needed, do not set<br>any of the bits. More than 1 bit can be set, and it is up to<br>the host to decide the sequence of action(s) to take. Use<br>Bit 0 if possible. If Bit 0 is not possible then use Bit 1, etc.<br>**Bit**<br>**Bit Description**<br>7:6 Reserved. Shall be cleared to zero.<br>5 <br>PCIe Conventional Hot Reset.<br>4 <br>Main Power Cycle.<br>3 <br>PERST#.<br>2 <br>PCIe Function Level Reset.<br>1 <br>NVM Subsystem Reset.<br>0 <br>NVMe Controller Reset.|
|EREC-15|30|Device<br>Recovery<br>Action 2<br>Timeout|1|The amount of time the host should wait for the device to<br>complete the Device Recovery Action 2 in seconds<br>(overrides CAP.TO value).|
|EREC-16|31|Panic /<br>Assert<br>Count|1|The number of Panics / Asserts the device has encountered<br>during its lifetime. This is a saturating counter.|
|EREC-17|63:32|Previous<br>Panic IDs|32|This set of fields reports the four most recent Panic IDs not<br>including the ID of the current panic.<br>**Byte Byte Description**<br>39:32 Panic ID N-1<br>47:40 Panic ID N-2<br>55:48 Panic ID N-3<br>63:56 Panic ID N-4|
|EREC-10|493:64|Reserved|430|Shall be cleared to zero.|
|EREC-11|495:494|Log Page<br>Version|2|This indicates the version of the mapping this log page<br>uses. Shall be set to 0003h.|
|EREC-12|511:496|Log Page<br>GUID|16|Shall be set to 5A1983BA3DFD4DABAE3430FE2131D944h.|

|Byte|Byte Description|
|---|---|
|39:32|Panic ID N-1|
|47:40|Panic ID N-2|
|55:48|Panic ID N-3|
|63:56|Panic ID N-4|

**4.8.8 Latency Monitor Log Page and Feature Set Requirements**

The following are requirements for the Latency Monitor log page and Latency Monitor Feature Set. For
more information about the Latency Monitoring Feature Set (see Section 22 Latency Monitoring Feature
Set Theory of Operation).

|Requirement ID|Description|
|---|---|
|LMLOG-1|All values in the Latency Monitor log page shall be persistent across power cycles and<br>resets unless otherwise specified.|
|LMLOG-2|All counters shall be saturating counters (i.e., if the counter reaches the maximum<br>allowable size, it stops incrementing and does NOT roll back to 0).|

<!-- page 45 -->
|Requirement ID|Description|
|---|---|
|LMLOG-3|All values in the Latency Monitor log page shall be little endian format.|
|LMLOG-4|A read of the Latency Monitor log page shall be a simple read of the active data and shall<br>not block IO.|
|LMLOG-5|Data in the Latency Monitor log page which is read by the host shall be no more than 10<br>minutes old.|
|LMLOG-6|When configuring the Latency Monitoring Feature with Set Features the Active Buckets<br>and Static Buckets shall be reset.|
|LMLOG-7|When powering on, the counters shall run based on the previously configured values.  If<br>the values have never been configured, they shall run based on the default values.|
|LMLOG-8|The Latency Stamp shall be based on the NVMe timestamp set by the last Timestamp<br>(Feature 0Eh) Set Features command if any.  If a NVMe Timestamp (Feature 0Eh) Set<br>Features command has not been received, then the Latency Stamp shall be based on the<br>device power on hours.|
|LMLOG-9|When the device provides a Latency Stamp of latency outliers, the Latency Stamp shall be<br>based on command completion.|
|LMLOG-10|When generating a Latency Monitoring log page (Feature Identifier C5h), the latency shall<br>be no greater than the latency associated with generating a Telemetry Controller-Initiated<br>log page (Feature Identifier 08h) or a Telemetry Host-Initiated log page (Feature Identifier<br>07h).|
|LMLOG-11|When configuring this feature, the thresholds shall always be configured such that Active<br>Threshold A < Active Threshold B < Active Threshold C < Active Threshold D.  If the host<br>attempts to configure the device in such a way that violates the above rules, the device<br>shall return Invalid Field in Command.|
|LMLOG-12|The device shall support the Latency Monitoring Feature Set.|
|LMLOG-13|The Latency Monitor Log page shall be 512 bytes.|
|LMLOG-14|Executing a Set Features command for Latency Monitor log page (Feature Identifier C5h)<br>shall reset all the contents in the Active/Static Buckets.|

**4.8.9 Latency Monitor (Log Identifier C3h)**

This log page shall be 512 bytes with the following functional requirements and field format (see Section
22 Latency Monitoring Feature Set Theory of Operation for additional details):

<!-- page 46 -->
|Col1|Field Description|
|---|---|
|Bit|Bit Description|
|7:3|Reserved.  Shall be cleared to zero.|
|2|Active Measured Latency Supported.<br>When set to 1b the Active Measured Latency field<br>is supported and shall be populated based on the<br>Active Latency Configuration settings.  When<br>cleared to 0b the Active Measured Latency is not<br>supported.|
|1|Active Latency Configuration/Active Latency Mode<br>1 Supported.<br>When set to 1b the device shall support the Active<br>Latency Configuration with the Active Latency<br>Mode = 1b.  When cleared to 0b the device does<br>not support Active Latency Mode =1b.|
|0|Latency Monitoring Feature Enabled.<br>This is a global feature enable.  When set to 1b the<br>Latency Monitoring Feature for this device is<br>enabled.  When cleared to 0b all features in the<br>Latency Monitoring Log page are disabled for this<br>device and can be ignored.  When cleared to 0b<br>the other fields in this log page are not power loss<br>safe and may be lost.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-1|0|Latency<br>Monitor<br>Feature<br>Status|1|Bit <br>Bit Description <br>7:3 Reserved. Shall be cleared to zero.<br>2 <br>Active Measured Latency Supported.<br>When set to 1b the Active Measured Latency field<br>is supported and shall be populated based on the<br>Active Latency Configuration settings. When<br>cleared to 0b the Active Measured Latency is not<br>supported.<br>1 <br>Active Latency Configuration/Active Latency Mode<br>1 Supported.<br>When set to 1b the device shall support the Active<br>Latency Configuration with the Active Latency<br>Mode = 1b. When cleared to 0b the device does<br>not support Active Latency Mode =1b.<br>0 <br>Latency Monitoring Feature Enabled.<br>This is a global feature enable. When set to 1b the<br>Latency Monitoring Feature for this device is<br>enabled. When cleared to 0b all features in the<br>Latency Monitoring Log page are disabled for this<br>device and can be ignored. When cleared to 0b<br>the other fields in this log page are not power loss<br>safe and may be lost.<br>The default value shall be 07h.|
|LMDATA-2|1|Reserved|1|Shall be cleared to zero.|
|LMDATA-3|3:2|Active<br>Bucket<br>Timer|2|The Active Bucket Timer is in 5-minute increments. Thus, a<br>value of 0001h is 5 minutes and a value of 0002h is 10<br>minutes. This represents the amount of time the Active<br>Buckets have been accumulating data. The Active Bucket<br>Timer will saturate at FFFFh. When the Active Bucket Timer<br>reaches the Active Bucket Timer Threshold then the data<br>specified inSection 22 Latency Monitoring Feature Set<br>Theory of Operation is moved into the Static Buckets, the<br>Active Bucket Timer is cleared to 0000h and restarts<br>counting. If the Active Bucket Timer is running and there is a<br>power cycle the Active Bucket Timer value from before the<br>power cycle shall be restored into the Active Bucket Timer<br>and the Active Bucket Timer shall continue when the device<br>is powered on.|

<!-- page 47 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-4|5:4|Active<br>Bucket<br>Timer<br>Threshold|2|Active Bucket Timer Threshold is the threshold used to<br>compare with the Active Bucket Timer. When cleared to<br>0000h this threshold is not used, the Active Bucket Timer<br>will saturate, and the Static Buckets will not be loaded. This<br>threshold is in 5-minute increments.<br>The factory default value of the Active Bucket Timer<br>Threshold shall be set to 07E0h.|
|LMDATA-5|6|Active<br>Threshold<br>A|1|This defines Active Threshold A. This is in 5 ms increments.<br>A value of 00h represents 5 ms. A value of FFh represents<br>1.280 seconds. The factory default is 05h.|
|LMDATA-6|7|Active<br>Threshold<br>B|1|This is in 5 ms increments. The factory default is 13h.|
|LMDATA-7|8|Active<br>Threshold<br>C|1|This is in 5 ms increments. The factory default is 1Eh.|
|LMDATA-8|9|Active<br>Threshold<br>D|1|This is in 5 ms increments. The factory default is 2Eh.|

<!-- page 48 -->
|Bit|Bucket|Counter|Bit Description|
|---|---|---|---|
|15:12|N/A|N/A|Reserved.  Shall be<br>cleared to zero.|
|11|3|Deallocate/<br>TRIM|Active Latency Mode<br>[11]|
|10|3|Write|Active Latency Mode<br>[10]|
|9|3|Read|Active Latency Mode<br>[9]|
|8|2|Deallocate/<br>TRIM|Active Latency Mode<br>[8]|
|7|2|Write|Active Latency Mode<br>[7]|
|6|2|Read|Active Latency Mode<br>[6]|
|5|1|Deallocate/<br>TRIM|Active Latency Mode<br>[5]|
|4|1|Write|Active Latency Mode<br>[4]|
|3|1|Read|Active Latency Mode<br>[3]|
|2|0|Deallocate/<br>TRIM|Active Latency Mode<br>[2]|
|1|0|Write|Active Latency Mode<br>[1]|
|0|0|Read|Active Latency Mode<br>[0]|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-9|11:10|Active<br>Latency<br>Configurat<br>ion|2|This configures how both the Active Latency Stamp, and the<br>Active Measured Latency Fields are updated on a per I/O<br>command (Read, Write, Deallocate) counter basis.<br>When the Active Latency Mode is cleared to 0b the Active<br>Latency Stamp and the Active Measured Latency will trigger<br>and update the first time the associated command counter<br>increments.  Once this trigger happens the fields shall not be<br>updated until the Active Latency Stamp and Active<br>Measured Latency fields are reset based on the Active<br>Bucket Timer expiring.<br>When the Active Latency Mode is set to 1b the Active<br>Latency Stamp and the Active Measured Latency fields shall<br>update to show the largest measured latency based on the<br>associated command counter.<br>**Bit**<br>**Bucket**<br>**Counter**<br>**Bit Description**<br>15:12<br>N/A<br>N/A<br>Reserved.  Shall be<br>cleared to zero.<br>11<br>3 <br>Deallocate/<br>TRIM<br>Active Latency Mode<br>[11]<br>10<br>3 <br>Write<br>Active Latency Mode<br>[10]<br>9 <br>3 <br>Read<br>Active Latency Mode<br>[9]<br>8 <br>2 <br>Deallocate/<br>TRIM<br>Active Latency Mode<br>[8]<br>7 <br>2 <br>Write<br>Active Latency Mode<br>[7]<br>6 <br>2 <br>Read<br>Active Latency Mode<br>[6]<br>5 <br>1 <br>Deallocate/<br>TRIM<br>Active Latency Mode<br>[5]<br>4 <br>1 <br>Write<br>Active Latency Mode<br>[4]<br>3 <br>1 <br>Read<br>Active Latency Mode<br>[3]<br>2 <br>0 <br>Deallocate/<br>TRIM<br>Active Latency Mode<br>[2]<br>1 <br>0 <br>Write<br>Active Latency Mode<br>[1]<br>0 <br>0 <br>Read<br>Active Latency Mode<br>[0]<br>The default value shall be 0FFFh.|

<!-- page 49 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
|LMDATA-10|12|Active<br>Latency<br>Minimum<br>Window|1|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|This is the minimum number of 100 ms increments between<br>Latency Events for a single Active Latency Stamp and Active<br>Measured Latency.  When cleared to 00h this feature is<br>disabled.  This count is in 100 ms increments, thus a value of<br>01h is 100 ms and 02h is 200 ms.  Once a Latency<br>Stamp/Measured Latency is updated if the Active Latency<br>Minimum Window time has not expired and an event that is<br>configurated to generate a Latency Stamp/Measured<br>Latency occurs the Latency Stamp/Measured Latency will<br>not be recorded.  The default value of this field is 0Ah.|
|LMDATA-11|31:13|Reserved|19|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|
|LMDATA-12|47:32|Active<br>Bucket<br>Counter 0|16|||**Byte**<br>**Address**|**Byte Description**|**Byte Description**|||
|LMDATA-12|47:32|Active<br>Bucket<br>Counter 0|16|||47:44|Read Command Counter.|Read Command Counter.|Read Command Counter.|Read Command Counter.|
|LMDATA-12|47:32|Active<br>Bucket<br>Counter 0|16|||43:40|Write Command Counter.|Write Command Counter.|Write Command Counter.|Write Command Counter.|
|LMDATA-12|47:32|Active<br>Bucket<br>Counter 0|16|||39:36|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|
|LMDATA-12|47:32|Active<br>Bucket<br>Counter 0|16|||35:32|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|
|LMDATA-13|63:48|Active<br>Bucket<br>Counter 1|16|||**Byte**<br>**Address**|**Byte Description**|**Byte Description**|||
|LMDATA-13|63:48|Active<br>Bucket<br>Counter 1|16|||63:60|Read Command Counter.|Read Command Counter.|Read Command Counter.|Read Command Counter.|
|LMDATA-13|63:48|Active<br>Bucket<br>Counter 1|16|||59:56|Write Command Counter.|Write Command Counter.|Write Command Counter.|Write Command Counter.|
|LMDATA-13|63:48|Active<br>Bucket<br>Counter 1|16|||55:52|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|
|LMDATA-13|63:48|Active<br>Bucket<br>Counter 1|16|||51:48|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|
|LMDATA-14|79:64|Active<br>Bucket<br>Counter 2|16|||**Byte**<br>**Address**|**Byte Description**|**Byte Description**|||
|LMDATA-14|79:64|Active<br>Bucket<br>Counter 2|16|||79:76|Read Command Counter.|Read Command Counter.|Read Command Counter.|Read Command Counter.|
|LMDATA-14|79:64|Active<br>Bucket<br>Counter 2|16|||75:72|Write Command Counter.|Write Command Counter.|Write Command Counter.|Write Command Counter.|
|LMDATA-14|79:64|Active<br>Bucket<br>Counter 2|16|||71:68|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|
|LMDATA-14|79:64|Active<br>Bucket<br>Counter 2|16|||67:64|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|
|LMDATA-15|95:80|Active<br>Bucket<br>Counter 3|16||**Byte**<br>**Address**|**Byte**<br>**Address**|**Byte**<br>**Address**|**Byte Description**|**Byte Description**||
|LMDATA-15|95:80|Active<br>Bucket<br>Counter 3|16||95:92|95:92|95:92|Read Command Counter.|Read Command Counter.|Read Command Counter.|
|LMDATA-15|95:80|Active<br>Bucket<br>Counter 3|16||91:88|91:88|91:88|Write Command Counter.|Write Command Counter.|Write Command Counter.|
|LMDATA-15|95:80|Active<br>Bucket<br>Counter 3|16||87:84|87:84|87:84|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|Deallocate/TRIM Command Counter.|
|LMDATA-15|95:80|Active<br>Bucket<br>Counter 3|16||83:80|83:80|83:80|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|

<!-- page 50 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-16|191:96|Active<br>Latency<br>Stamp<br>|96|This field contains a Timestamp for when a latency event<br>occurred for each counter.  A value of FFFFFFFF_FFFFFFFFh<br>means the Latency Stamp is not valid.  The Active Latency<br>Stamp uses the data format for Timestamp as defined in the<br>NVM Express Base Specification.<br>**Byte**<br>**Address**<br>**Bucket**<br>**Counter**<br>**Byte**<br>**Description**<br>191:184<br>0 <br>Read<br>Active Latency<br>Stamp 0<br>183:176<br>0 <br>Write<br>Active Latency<br>Stamp 1<br>175:168<br>0 <br>Deallocate/TRIMActive Latency<br>Stamp 2<br>167:160<br>1 <br>Read<br>Active Latency<br>Stamp 3<br>159:152<br>1 <br>Write<br>Active Latency<br>Stamp 4<br>151:144<br>1 <br>Deallocate/TRIMActive Latency<br>Stamp 5<br>143:136<br>2 <br>Read<br>Active Latency<br>Stamp 6<br>135:128<br>2 <br>Write<br>Active Latency<br>Stamp 7<br>127:120<br>2 <br>Deallocate/TRIMActive Latency<br>Stamp 8<br>119:112<br>3 <br>Read<br>Active Latency<br>Stamp 9<br>111:104<br>3 <br>Write<br>Active Latency<br>Stamp 10<br>103:96<br>3 <br>Deallocate/TRIMActive Latency<br>Stamp 11|

|Byte<br>Address|Bucket|Counter|Byte<br>Description|
|---|---|---|---|
|191:184|0|Read|Active Latency<br>Stamp 0|
|183:176|0|Write|Active Latency<br>Stamp 1|
|175:168|0|Deallocate/TRIM|Active Latency<br>Stamp 2|
|167:160|1|Read|Active Latency<br>Stamp 3|
|159:152|1|Write|Active Latency<br>Stamp 4|
|151:144|1|Deallocate/TRIM|Active Latency<br>Stamp 5|
|143:136|2|Read|Active Latency<br>Stamp 6|
|135:128|2|Write|Active Latency<br>Stamp 7|
|127:120|2|Deallocate/TRIM|Active Latency<br>Stamp 8|
|119:112|3|Read|Active Latency<br>Stamp 9|
|111:104|3|Write|Active Latency<br>Stamp 10|
|103:96|3|Deallocate/TRIM|Active Latency<br>Stamp 11|

<!-- page 51 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-17|215:192|Active<br>Measured<br>Latency|24|This is the measured latency that caused the counter to<br>increment.  A value of 0000h means this field is invalid.  A<br>value of 0001h represents 1 ms.  A value of 0002h<br>represents 2 ms.<br>**Byte**<br>**Address**<br>**Bucket**<br>**Counter**<br>**Byte**<br>**Description**<br>215:214<br>0 <br>Read<br>Active<br>Measured<br>Latency 0<br>213:212<br>0 <br>Write<br>Active<br>Measured<br>Latency 1<br>211:210<br>0 <br>Deallocate/TRIM<br>Active<br>Measured<br>Latency 2<br>209:208<br>1 <br>Read<br>Active<br>Measured<br>Latency 3<br>207:206<br>1 <br>Write<br>Active<br>Measured<br>Latency 4<br>205:204<br>1 <br>Deallocate/TRIM<br>Active<br>Measured<br>Latency 5<br>203:202<br>2 <br>Read<br>Active<br>Measured<br>Latency 6<br>201:200<br>2 <br>Write<br>Active<br>Measured<br>Latency 7<br>199:198<br>2 <br>Deallocate/TRIM<br>Active<br>Measured<br>Latency 8<br>197:196<br>3 <br>Read<br>Active<br>Measured<br>Latency 9<br>195:194<br>3 <br>Write<br>Active<br>Measured<br>Latency 10<br>193:192<br>3 <br>Deallocate/TRIM<br>Active<br>Measured<br>Latency 11|

|Byte<br>Address|Bucket|Counter|Byte<br>Description|
|---|---|---|---|
|215:214|0|Read|Active<br>Measured<br>Latency 0|
|213:212|0|Write|Active<br>Measured<br>Latency 1|
|211:210|0|Deallocate/TRIM|Active<br>Measured<br>Latency 2|
|209:208|1|Read|Active<br>Measured<br>Latency 3|
|207:206|1|Write|Active<br>Measured<br>Latency 4|
|205:204|1|Deallocate/TRIM|Active<br>Measured<br>Latency 5|
|203:202|2|Read|Active<br>Measured<br>Latency 6|
|201:200|2|Write|Active<br>Measured<br>Latency 7|
|199:198|2|Deallocate/TRIM|Active<br>Measured<br>Latency 8|
|197:196|3|Read|Active<br>Measured<br>Latency 9|
|195:194|3|Write|Active<br>Measured<br>Latency 10|
|193:192|3|Deallocate/TRIM|Active<br>Measured<br>Latency 11|

<!-- page 52 -->
|Bit|Bucket|Counter|Bit Description|
|---|---|---|---|
|15:12|N/A|N/A|Reserved.  Shall be<br>cleared to zero.|
|11|3|Deallocate/<br>TRIM|Active Latency Stamp<br>Unit [11]|
|10|3|Write|Active Latency Stamp<br>Unit [10]|
|9|3|Read|Active Latency Stamp<br>Unit [9]|
|8|2|Deallocate/<br>TRIM|Active Latency Stamp<br>Unit [8]|
|7|2|Write|Active Latency Stamp<br>Unit [7]|
|6|2|Read|Active Latency Stamp<br>Unit [6]|
|5|1|Deallocate/<br>TRIM|Active Latency Stamp<br>Unit [5]|
|4|1|Write|Active Latency Stamp<br>Unit [4]|
|3|1|Read|Active Latency Stamp<br>Unit [3]|
|2|0|Deallocate/<br>TRIM|Active Latency Stamp<br>Unit [2]|
|1|0|Write|Active Latency Stamp<br>Unit [1]|
|0|0|Read|Active Latency Stamp<br>Unit [0]|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-18|217:216|Active<br>Latency<br>Stamp<br>Units|2|When bit is set to 1b, the Active Latency Stamp was based<br>on receiving the NVMe Timestamp.  When bit is cleared to<br>0b the Active Latency Stamp was based on power on hours<br>since the NVMe Timestamp was not received.<br>**Bit**<br>**Bucket**<br>**Counter**<br>**Bit Description**<br>15:12<br>N/A<br>N/A<br>Reserved.  Shall be<br>cleared to zero.<br>11<br>3 <br>Deallocate/<br>TRIM<br>Active Latency Stamp<br>Unit [11]<br>10<br>3 <br>Write<br>Active Latency Stamp<br>Unit [10]<br>9 <br>3 <br>Read<br>Active Latency Stamp<br>Unit [9]<br>8 <br>2 <br>Deallocate/<br>TRIM<br>Active Latency Stamp<br>Unit [8]<br>7 <br>2 <br>Write<br>Active Latency Stamp<br>Unit [7]<br>6 <br>2 <br>Read<br>Active Latency Stamp<br>Unit [6]<br>5 <br>1 <br>Deallocate/<br>TRIM<br>Active Latency Stamp<br>Unit [5]<br>4 <br>1 <br>Write<br>Active Latency Stamp<br>Unit [4]<br>3 <br>1 <br>Read<br>Active Latency Stamp<br>Unit [3]<br>2 <br>0 <br>Deallocate/<br>TRIM<br>Active Latency Stamp<br>Unit [2]<br>1 <br>0 <br>Write<br>Active Latency Stamp<br>Unit [1]<br>0 <br>0 <br>Read<br>Active Latency Stamp<br>Unit [0]|
|LMDATA-19|239:218|Reserved|22|Shall be cleared to zero.|
|LMDATA-20|255:240|Static<br>Bucket<br>Counter 0|16|This is a snapshot of the Active Bucket Counter 0 which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>**Byte**<br>**Address**<br>**Byte Description**<br>255:252<br>Read Command Counter.<br>251:248<br>Write Command Counter.<br>247:244<br>Deallocate/TRIM Command Counter.<br>243:240<br>Reserved.  Shall be cleared to zero.|

|Byte<br>Address|Byte Description|
|---|---|
|255:252|Read Command Counter.|
|251:248|Write Command Counter.|
|247:244|Deallocate/TRIM Command Counter.|
|243:240|Reserved.  Shall be cleared to zero.|

<!-- page 53 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-21|271:256|Static<br>Bucket<br>Counter 1|16|This is a snapshot of the Active Bucket Counter 1 which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>**Byte**<br>**Address**<br>**Byte Description**<br>271:268<br>Read Command Counter.<br>267:264<br>Write Command Counter.<br>263:260<br>Deallocate/TRIM Command Counter.<br>259:256<br>Reserved. Shall be cleared to zero.|
|LMDATA-22|287:272|Static<br>Bucket<br>Counter 2|16|This is a snapshot of the Active Bucket Counter 2 which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>**Byte**<br>**Address**<br>**Byte Description**<br>287:284<br>Read Command Counter.<br>283:280<br>Write Command Counter.<br>279:276<br>Deallocate/TRIM Command Counter.<br>275:272<br>Reserved. Shall be cleared to zero.|
|LMDATA-23|303:288|Static<br>Bucket<br>Counter 3|16|This is a snapshot of the Active Bucket Counter 3 which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>**Byte**<br>**Address**<br>**Byte Description**<br>303:300<br>Read Command Counter.<br>299:296<br>Write Command Counter.<br>295:292<br>Deallocate/TRIM Command Counter.<br>291:288<br>Reserved. Shall be cleared to zero.|

53

|Byte<br>Address|Byte Description|
|---|---|
|271:268|Read Command Counter.|
|267:264|Write Command Counter.|
|263:260|Deallocate/TRIM Command Counter.|
|259:256|Reserved.  Shall be cleared to zero.|

|Byte<br>Address|Byte Description|
|---|---|
|287:284|Read Command Counter.|
|283:280|Write Command Counter.|
|279:276|Deallocate/TRIM Command Counter.|
|275:272|Reserved.  Shall be cleared to zero.|

|Byte<br>Address|Byte Description|
|---|---|
|303:300|Read Command Counter.|
|299:296|Write Command Counter.|
|295:292|Deallocate/TRIM Command Counter.|
|291:288|Reserved.  Shall be cleared to zero.|

<!-- page 54 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-24|399:304|Static<br>Latency<br>Stamp|96|This is a snapshot of the Active Latency Stamp which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>This field contains a timestamp for when a latency event<br>occurred for each counter.  A value of FFFFFFFF_FFFFFFFFh<br>means the Latency Stamp is not valid.  The Static Latency<br>Stamp uses the Timestamp data format as defined in the<br>NVM Express Base Specification.<br>**Byte**<br>**Address**<br>**Bucket**<br>**Counter**<br>**Byte**<br>**Description**<br>399:392<br>0 <br>Read<br>Static Latency<br>Stamp 0<br>391:384<br>0 <br>Write<br>Static Latency<br>Stamp 1<br>383:376<br>0 <br>Deallocate/TRIMStatic Latency<br>Stamp 2<br>375:368<br>1 <br>Read<br>Static Latency<br>Stamp 3<br>367:360<br>1 <br>Write<br>Static Latency<br>Stamp 4<br>359:352<br>1 <br>Deallocate/TRIMStatic Latency<br>Stamp 5<br>351:344<br>2 <br>Read<br>Static Latency<br>Stamp 6<br>343:336<br>2 <br>Write<br>Static Latency<br>Stamp 7<br>335:328<br>2 <br>Deallocate/TRIMStatic Latency<br>Stamp 8<br>327:320<br>3 <br>Read<br>Static Latency<br>Stamp 9<br>319:312<br>3 <br>Write<br>Static Latency<br>Stamp 10<br>311:304<br>3 <br>Deallocate/TRIMStatic Latency<br>Stamp 11|

|Byte<br>Address|Bucket|Counter|Byte<br>Description|
|---|---|---|---|
|399:392|0|Read|Static Latency<br>Stamp 0|
|391:384|0|Write|Static Latency<br>Stamp 1|
|383:376|0|Deallocate/TRIM|Static Latency<br>Stamp 2|
|375:368|1|Read|Static Latency<br>Stamp 3|
|367:360|1|Write|Static Latency<br>Stamp 4|
|359:352|1|Deallocate/TRIM|Static Latency<br>Stamp 5|
|351:344|2|Read|Static Latency<br>Stamp 6|
|343:336|2|Write|Static Latency<br>Stamp 7|
|335:328|2|Deallocate/TRIM|Static Latency<br>Stamp 8|
|327:320|3|Read|Static Latency<br>Stamp 9|
|319:312|3|Write|Static Latency<br>Stamp 10|
|311:304|3|Deallocate/TRIM|Static Latency<br>Stamp 11|

<!-- page 55 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-25|423:400|Static<br>Measured<br>Latency|24|This is a snapshot of the Active Measured Latency which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>A value of 0000h means this field is invalid.  A value of 0001h<br>represents 1 ms.  A value of 0002h represents 2 ms.<br>**Byte**<br>**Address**<br>**Bucket**<br>**Counter**<br>**Byte**<br>**Description**<br>423:422<br>0 <br>Read<br>Static<br>Measured<br>Latency 0<br>421:420<br>0 <br>Write<br>Static<br>Measured<br>Latency 1<br>419:418<br>0 <br>Deallocate/TRIM<br>Static<br>Measured<br>Latency 2<br>417:416<br>1 <br>Read<br>Static<br>Measured<br>Latency 3<br>415:414<br>1 <br>Write<br>Static<br>Measured<br>Latency 4<br>413:412<br>1 <br>Deallocate/TRIM<br>Static<br>Measured<br>Latency 5<br>411:410<br>2 <br>Read<br>Static<br>Measured<br>Latency 6<br>409:408<br>2 <br>Write<br>Static<br>Measured<br>Latency 7<br>407:406<br>2 <br>Deallocate/TRIM<br>Static<br>Measured<br>Latency 8<br>405:404<br>3 <br>Read<br>Static<br>Measured<br>Latency 9<br>403:402<br>3 <br>Write<br>Static<br>Measured<br>Latency 10<br>401:400<br>3 <br>Deallocate/TRIM<br>Static<br>Measured<br>Latency 11|

|Byte<br>Address|Bucket|Counter|Byte<br>Description|
|---|---|---|---|
|423:422|0|Read|Static<br>Measured<br>Latency 0|
|421:420|0|Write|Static<br>Measured<br>Latency 1|
|419:418|0|Deallocate/TRIM|Static<br>Measured<br>Latency 2|
|417:416|1|Read|Static<br>Measured<br>Latency 3|
|415:414|1|Write|Static<br>Measured<br>Latency 4|
|413:412|1|Deallocate/TRIM|Static<br>Measured<br>Latency 5|
|411:410|2|Read|Static<br>Measured<br>Latency 6|
|409:408|2|Write|Static<br>Measured<br>Latency 7|
|407:406|2|Deallocate/TRIM|Static<br>Measured<br>Latency 8|
|405:404|3|Read|Static<br>Measured<br>Latency 9|
|403:402|3|Write|Static<br>Measured<br>Latency 10|
|401:400|3|Deallocate/TRIM|Static<br>Measured<br>Latency 11|

<!-- page 56 -->
|Bit|Bucket|Counter|Byte Description|
|---|---|---|---|
|15:12|N/A|N/A|Reserved.  Shall be<br>cleared to zero.|
|11|3|Deallocate/<br>TRIM|Static Latency Stamp<br>Unit [11]|
|10|3|Write|Static Latency Stamp<br>Unit [10]|
|9|3|Read|Static Latency Stamp<br>Unit [9]|
|8|2|Deallocate/<br>TRIM|Static Latency Stamp<br>Unit [8]|
|7|2|Write|Static Latency Stamp<br>Unit [7]|
|6|2|Read|Static Latency Stamp<br>Unit [6]|
|5|1|Deallocate/<br>TRIM|Static Latency Stamp<br>Unit [5]|
|4|1|Write|Static Latency Stamp<br>Unit [4]|
|3|1|Read|Static Latency Stamp<br>Unit [3]|
|2|0|Deallocate/<br>TRIM|Static Latency Stamp<br>Unit [2]|
|1|0|Write|Static Latency Stamp<br>Unit [1]|
|0|0|Read|Static Latency Stamp<br>Unit [0]|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-26|425:424|Static<br>Latency<br>Stamp<br>Units|2|This is a snapshot of the Active Latency Stamp Units which is<br>moved to this field when the Active Bucket Timer equals the<br>Active Bucket Timer Threshold.<br>When bit is set to 1b the Static Latency Stamp was based on<br>receiving the NVMe Timestamp and the offset from this.<br>When bit is cleared to 0b the Static Latency Stamp was<br>based on power on hours since the NVMe Timestamp was<br>not received.<br>**Bit**<br>**Bucket**<br>**Counter**<br>**Byte Description**<br>15:12<br>N/A<br>N/A<br>Reserved. Shall be<br>cleared to zero.<br>11<br>3 <br>Deallocate/<br>TRIM<br>Static Latency Stamp<br>Unit [11]<br>10<br>3 <br>Write<br>Static Latency Stamp<br>Unit [10]<br>9 <br>3 <br>Read<br>Static Latency Stamp<br>Unit [9]<br>8 <br>2 <br>Deallocate/<br>TRIM<br>Static Latency Stamp<br>Unit [8]<br>7 <br>2 <br>Write<br>Static Latency Stamp<br>Unit [7]<br>6 <br>2 <br>Read<br>Static Latency Stamp<br>Unit [6]<br>5 <br>1 <br>Deallocate/<br>TRIM<br>Static Latency Stamp<br>Unit [5]<br>4 <br>1 <br>Write<br>Static Latency Stamp<br>Unit [4]<br>3 <br>1 <br>Read<br>Static Latency Stamp<br>Unit [3]<br>2 <br>0 <br>Deallocate/<br>TRIM<br>Static Latency Stamp<br>Unit [2]<br>1 <br>0 <br>Write<br>Static Latency Stamp<br>Unit [1]<br>0 <br>0 <br>Read<br>Static Latency Stamp<br>Unit [0]|
|LMDATA-27|435:426|Reserved|10|Shall be cleared to zero.|
|LMDATA-37|447:436|Latency<br>Monitor<br>Debug<br>Telemetry<br>Log Size|12|This is the number of Dwords in the Latency Monitor Debug<br>Log. This value is in Dwords.|

<!-- page 57 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-28|449:448|Debug Log<br>Trigger<br>Enable|2|This controls what counters can cause a debug log event to<br>be triggered. When set to 1b the first time the<br>bucket/counter combination is incremented a debug log is<br>triggered. When cleared to 0b a debug log will not be<br>triggered when the bucket/counter combination is<br>incremented.<br>**Bit**<br>**Default**<br>**Value**<br>**Bucket**<br>**Counter**<br>**Bit Description**<br>15:1<br>2 <br>N/A<br>N/A<br>N/A<br>Reserved.<br>Shall be<br>cleared to<br>zero.<br>11<br>0b<br>3 <br>Deallocate<br>/TRIM<br>Active Log<br>Enable [11]<br>10<br>0b<br>3 <br>Write<br>Active Log<br>Enable [10]<br>9 <br>0b<br>3 <br>Read<br>Active Log<br>Enable [9]<br>8 <br>0b<br>2 <br>Deallocate<br>/TRIM<br>Active Log<br>Enable [8]<br>7 <br>0b<br>2 <br>Write<br>Active Log<br>Enable [7]<br>6 <br>0b<br>2 <br>Read<br>Active Log<br>Enable [6]<br>5 <br>0b<br>1 <br>Deallocate<br>/TRIM<br>Active Log<br>Enable [5]<br>4 <br>0b<br>1 <br>Write<br>Active Log<br>Enable [4]<br>3 <br>0b<br>1 <br>Read<br>Active Log<br>Enable [3]<br>2 <br>0b<br>0 <br>Deallocate<br>/TRIM<br>Active Log<br>Enable [2]<br>1 <br>0b<br>0 <br>Write<br>Active Log<br>Enable [1]<br>0 <br>0b<br>0 <br>Read<br>Active Log<br>Enable [0]|
|LMDATA-29|451:450|Debug Log<br>Measured<br>Latency|2|When a debug log is triggered, this is the measured latency<br>for the Latency Stamp that caused the debug log to trigger.<br>A value of 0000h means this field is invalid. A value of 0001h<br>represents 1 ms. A value of 0002h represents 2 ms. A value<br>of FFFFh means the Debug Log Measured Latency saturated<br>at the max.|

|Bit|Default<br>Value|Bucket|Counter|Bit Description|
|---|---|---|---|---|
|15:1<br>2|N/A|N/A|N/A|Reserved.<br>Shall be<br>cleared to<br>zero.|
|11|0b|3|Deallocate<br>/TRIM|Active Log<br>Enable [11]|
|10|0b|3|Write|Active Log<br>Enable [10]|
|9|0b|3|Read|Active Log<br>Enable [9]|
|8|0b|2|Deallocate<br>/TRIM|Active Log<br>Enable [8]|
|7|0b|2|Write|Active Log<br>Enable [7]|
|6|0b|2|Read|Active Log<br>Enable [6]|
|5|0b|1|Deallocate<br>/TRIM|Active Log<br>Enable [5]|
|4|0b|1|Write|Active Log<br>Enable [4]|
|3|0b|1|Read|Active Log<br>Enable [3]|
|2|0b|0|Deallocate<br>/TRIM|Active Log<br>Enable [2]|
|1|0b|0|Write|Active Log<br>Enable [1]|
|0|0b|0|Read|Active Log<br>Enable [0]|

<!-- page 58 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDATA-30|459:452|Debug Log<br>Latency<br>Stamp|8|This is the Latency Stamp associated with the debug log.|
|LMDATA-31|461:460|Debug Log<br>Pointer|2|This shall be set to CAh if the Latency Monitor Debug<br>Telemetry Log is valid.|
|LMDATA-32|463:462|Debug<br>Counter<br>Trigger<br>Source|2|When the Debug Counter Trigger Source bit is set to 1b the<br>debug log is valid, and this is the counter that triggered the<br>debug log.  When the Debug Counter Trigger Source bit is<br>cleared to 0b this is not the counter that triggered the debug<br>log.  No more than 1 bit in this field shall be set.  When the<br>Debug Counter Trigger Source is 0b the Debug Log Latency,<br>Debug Log Latency Stamp, Debug Log Pointer, and Debug<br>Counter Trigger Source is not valid.<br>If the debug log has been cleared this field shall be cleared<br>to zero.<br>**Bit**<br>**Bucket**<br>**Counter**<br>**Bit Description**<br>15:12<br>N/A<br>N/A<br>Reserved.  Shall<br>be cleared to<br>zero.<br>11<br>3 <br>Deallocate/ TRIM<br>Debug Counter<br>Trigger Source 11<br>10<br>3 <br>Write<br>Debug Counter<br>Trigger Source 10<br>9 <br>3 <br>Read<br>Debug Counter<br>Trigger Source 9<br>8 <br>2 <br>Deallocate/ TRIM<br>Debug Counter<br>Trigger Source 8<br>7 <br>2 <br>Write<br>Debug Counter<br>Trigger Source 7<br>6 <br>2 <br>Read<br>Debug Counter<br>Trigger Source 6<br>5 <br>1 <br>Deallocate/ TRIM<br>Debug Counter<br>Trigger Source 5<br>4 <br>1 <br>Write<br>Debug Counter<br>Trigger Source 4<br>3 <br>1 <br>Read<br>Debug Counter<br>Trigger Source 3<br>2 <br>0 <br>Deallocate/ TRIM<br>Debug Counter<br>Trigger Source 2<br>1 <br>0 <br>Write<br>Debug Counter<br>Trigger Source 1<br>0 <br>0 <br>Read<br>Debug Counter<br>Trigger Source 0|

|Bit|Bucket|Counter|Bit Description|
|---|---|---|---|
|15:12|N/A|N/A|Reserved.  Shall<br>be cleared to<br>zero.|
|11|3|Deallocate/ TRIM|Debug Counter<br>Trigger Source 11|
|10|3|Write|Debug Counter<br>Trigger Source 10|
|9|3|Read|Debug Counter<br>Trigger Source 9|
|8|2|Deallocate/ TRIM|Debug Counter<br>Trigger Source 8|
|7|2|Write|Debug Counter<br>Trigger Source 7|
|6|2|Read|Debug Counter<br>Trigger Source 6|
|5|1|Deallocate/ TRIM|Debug Counter<br>Trigger Source 5|
|4|1|Write|Debug Counter<br>Trigger Source 4|
|3|1|Read|Debug Counter<br>Trigger Source 3|
|2|0|Deallocate/ TRIM|Debug Counter<br>Trigger Source 2|
|1|0|Write|Debug Counter<br>Trigger Source 1|
|0|0|Read|Debug Counter<br>Trigger Source 0|

<!-- page 59 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|LMDATA-33|464|Debug Log<br>Stamp<br>Units|1||**Bit**|**Bit Description**||
|LMDATA-33|464|Debug Log<br>Stamp<br>Units|1||7:1|Reserved.  Shall be cleared to zero.|Reserved.  Shall be cleared to zero.|
|LMDATA-33|464|Debug Log<br>Stamp<br>Units|1||0|When set to 1b the Debug Latency Stamp was<br>based on receiving the NVMe Timestamp and the<br>offset from this.  When cleared to 0b the Debug<br>Latency Stamp was based on power on hours since<br>the NVMe Timestamp was not received.|When set to 1b the Debug Latency Stamp was<br>based on receiving the NVMe Timestamp and the<br>offset from this.  When cleared to 0b the Debug<br>Latency Stamp was based on power on hours since<br>the NVMe Timestamp was not received.|
|LMDATA-34|493:465|Reserved|29|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|
|LMDATA-35|495:494|Log Page<br>Version|2|This indicates the version of this log page.  Shall be set to<br>0004h.|This indicates the version of this log page.  Shall be set to<br>0004h.|This indicates the version of this log page.  Shall be set to<br>0004h.|This indicates the version of this log page.  Shall be set to<br>0004h.|
|LMDATA-36|511:496|Log Page<br>GUID|16|Shall be set to<br>85D45E58D4E643709C6C84D08CC07A92h.|Shall be set to<br>85D45E58D4E643709C6C84D08CC07A92h.|Shall be set to<br>85D45E58D4E643709C6C84D08CC07A92h.|Shall be set to<br>85D45E58D4E643709C6C84D08CC07A92h.|

**4.8.10 Device Capabilities (Log Identifier C4h) Requirements**

This log page provides the host with a consolidated report of critical device-specific support information.
This log page shall be 4096 bytes with the following functional requirements and field format:

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|DCLP-1|1:0|PCI Express<br>Ports|2|The number of physical PCI Express ports<br>supported by the device.|
|DCLP-2|3:2|OOB<br>Management<br>Support|2|Bit field indicating the OOB Management interfaces<br>supported by the device.<br>**Bit**<br>**Bit Description**<br>15<br>Shall be set to 1b if the device has been<br>tested and found to comply with the OOB<br>Management requirements of this<br>specification.<br>14:3 Reserved. Shall be cleared to zero.<br>2 <br>Shall be set to 1b if NVMe Basic<br>Management Command is supported.<br>1 <br>Shall be set to 1b if MCTP over PCIe VDM<br>is supported.<br>0 <br>Shall be set to 1b if MCTP over SMBus is<br>supported.|

|Bit|Bit Description|
|---|---|
|15|Shall be set to 1b if the device has been<br>tested and found to comply with the OOB<br>Management requirements of this<br>specification.|
|14:3|Reserved. Shall be cleared to zero.|
|2|Shall be set to 1b if NVMe Basic<br>Management Command is supported.|
|1|Shall be set to 1b if MCTP over PCIe VDM<br>is supported.|
|0|Shall be set to 1b if MCTP over SMBus is<br>supported.|

<!-- page 60 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|DCLP-3|5:4|Write Zeroes<br>Command<br>Support|2|Bit field indicating the Write Zeroes command<br>requirements supported by the device.<br>**Bit**<br>**Bit Description**<br>15<br>Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Write Zeroes command requirements of<br>this specification.<br>14:5 Reserved. Shall be cleared to zero.<br>4 <br>Shall be set to 1b if the requirements of<br>NVMe-IO-6 are met.<br>3 <br>Shall be set to 1b if the requirements of<br>NVMe-IO-5 are met.<br>2 <br>Shall be set to 1b if setting the FUA bit is<br>supported.<br>1 <br>Shall be set to 1b if setting the DEAC bit is<br>supported.<br>0 <br>Shall be set to 1b if the Write Zeroes<br>command is supported.|
|DCLP-4|7:6|Sanitize<br>Command<br>Support|2|Bit field indicating the Sanitize command<br>requirements supported by the device.<br>**Bit**<br>**Bit Description**<br>15<br>Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Sanitize command requirements of this<br>specification.<br>14:5 Reserved. Shall be cleared to zero.<br>4 <br>Shall be set to 1b if Deallocate LBAs is<br>supported.<br>3 <br>Shall be set to 1b if Overwrite is<br>supported.<br>2 <br>Shall be set to 1b if Block Erase is<br>supported.<br>1 <br>Shall be set to 1b if Crypto-Erase is<br>supported.<br>0 <br>Shall be set to 1b if the Sanitize command<br>is supported.|

|Bit|Bit Description|
|---|---|
|15|Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Write Zeroes command requirements of<br>this specification.|
|14:5|Reserved. Shall be cleared to zero.|
|4|Shall be set to 1b if the requirements of<br>NVMe-IO-6 are met.|
|3|Shall be set to 1b if the requirements of<br>NVMe-IO-5 are met.|
|2|Shall be set to 1b if setting the FUA bit is<br>supported.|
|1|Shall be set to 1b if setting the DEAC bit is<br>supported.|
|0|Shall be set to 1b if the Write Zeroes<br>command is supported.|

|Bit|Bit Description|
|---|---|
|15|Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Sanitize command requirements of this<br>specification.|
|14:5|Reserved. Shall be cleared to zero.|
|4|Shall be set to 1b if Deallocate LBAs is<br>supported.|
|3|Shall be set to 1b if Overwrite is<br>supported.|
|2|Shall be set to 1b if Block Erase is<br>supported.|
|1|Shall be set to 1b if Crypto-Erase is<br>supported.|
|0|Shall be set to 1b if the Sanitize command<br>is supported.|

<!-- page 61 -->
|Bit|Bit Description|
|---|---|
|15|Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Dataset Management command<br>requirements of this specification.|
|14:2|Reserved.  Shall be cleared to zero.|
|1|Shall be set to 1b if Attribute – Deallocate<br>(AD) is supported.|
|0|Shall be set to 1b if the Dataset<br>Management command is supported.|

|Bit|Bit Description|
|---|---|
|15|Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Write Uncorrectable command<br>requirements of this specification.|
|14:4|Reserved.  Shall be cleared to zero.|
|3|Shall be set to 1b if the SMART / Health<br>Information (Log Identifier 02h)<br>requirements ofNVMe-IO-14 are met.|
|2|<br>Shall be set to 1b if the device supports<br>setting uncorrectable on the maximum<br>number of LBAs allowed by the NVM<br>Express Base Specification.|
|1|Shall be set to 1b if the device supports<br>setting uncorrectable on a single LBA.|
|0|Shall be set to 1b if the Write<br>Uncorrectable command is supported.|

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|DCLP-5|9:8|Dataset<br>Management<br>Command<br>Support|2|Bit field indicating the Dataset Management<br>command requirements supported by the device.<br>**Bit**<br>**Bit Description**<br>15<br>Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Dataset Management command<br>requirements of this specification.<br>14:2 Reserved.  Shall be cleared to zero.<br>1 <br>Shall be set to 1b if Attribute – Deallocate<br>(AD) is supported.<br>0 <br>Shall be set to 1b if the Dataset<br>Management command is supported.|
|DCLP-6|11:10|Write<br>Uncorrectable<br>Command<br>Support|2|Bit field indicating the Write Uncorrectable<br>command requirements supported by the device.<br>**Bit**<br>**Bit Description**<br>15<br>Shall be set to 1b if the device has been<br>tested and found to comply with the<br>Write Uncorrectable command<br>requirements of this specification.<br>14:4 Reserved.  Shall be cleared to zero.<br>3 <br>Shall be set to 1b if the SMART / Health<br>Information (Log Identifier 02h)<br>requirements ofNVMe-IO-14 are met.<br>2 <br>Shall be set to 1b if the device supports<br>setting uncorrectable on the maximum<br>number of LBAs allowed by the NVM<br>Express Base Specification.<br>1 <br>Shall be set to 1b if the device supports<br>setting uncorrectable on a single LBA.<br>0 <br>Shall be set to 1b if the Write<br>Uncorrectable command is supported.|
|DCLP-7|13:12|Fused<br>Operation<br>Support<br>|2|Bit field indicating the fused command pairs<br>requirements supported by the device.<br>**Bit**<br>**Bit Description**<br>15<br>Shall be set to 1b if the device has been<br>tested and found to comply with the<br>fused command pair support<br>requirements of this specification.<br>14:1 Reserved.  Shall be cleared to zero.<br>0 <br>Shall be set to 1b if the Compare and<br>Write fused command pair is supported.|

|Bit|Bit Description|
|---|---|
|15|Shall be set to 1b if the device has been<br>tested and found to comply with the<br>fused command pair support<br>requirements of this specification.|
|14:1|Reserved.  Shall be cleared to zero.|
|0|Shall be set to 1b if the Compare and<br>Write fused command pair is supported.|

<!-- page 62 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|DCLP-8|15:14|Minimum<br>Valid DSSD<br>Power State|2|Shall be set to the lowest numbered valid DSSD<br>Power State.   Setting a DSSD Power State less than<br>this value results in Invalid Field in Command (see<br>DSSDPSS-2).|
|DCLP-9|143:16|DSSD Power<br>State<br>Descriptors|128|Byte 16 is reserved and shall be cleared to zero.<br>The device shall populate bytes 17-143 with a<br>single-byte DSSD Power State Descriptor for each<br>DSSD Power State (seeSection 4.8.11.1 DSSD<br>Power State Descriptor) starting with DSSD Power<br>State 1.<br>The DSSD Power State Descriptors shall be<br>populated in increasing order of power state<br>number, i.e., byte 17 contains the descriptor for<br>DSSD Power State 1, byte 18 contains the<br>descriptor for DSSD Power State 2, etc. up to byte<br>143 which contains the descriptor for DSSD Power<br>State 127.|
|DCLP-10|4077:144|Reserved|3934|Shall be cleared to zero.|
|DCLP-11|4079:4078|Log Page<br>Version|2|This indicates the version of the mapping this log<br>page uses.  Shall be set to 0001h.|
|DCLP-12|4095:4080|Log Page<br>GUID|16|Shall be set to<br>B7053C914B58495D98C9E1D10D054297h.|

**4.8.11 DSSD Power State Requirements**

DSSD power states provide an alternative interface to NVMe power management. DSSD and NVMe Power
States are numbered in opposite directions – higher numbered DSSD Power States consume more power
than lower numbered DSSD Power States, whereas higher numbered NVMe Power States consume less
power than lower numbered NVMe Power States.

Selecting a DSSD Power State via a Set Features command ( see Section 4.15.15 DSSD Power State (Feature
Identifier C7h) Set Feature) causes the device to run at the highest powered NVMe Power State whose
Maximum Power (MP) in watts is less than or equal to the number of the DSSD Power State. For example,
placing the device in DSSD Power State number 20 causes the device to enter the highest powered NVMe
Power State whose Maximum Power (MP) is less than or equal to 20 watts.

In general, a device will have more DSSD Power States than NVMe Power States. Selecting a DSSD Power
State whose number is not the Maximum Power (MP) in watts of an NVMe Power State causes the device to
drop down to run at the highest powered NVMe Power State whose Maximum Power (MP) does not exceed
the number of the DSSD Power State in watts.

For example, suppose that a device supports NVMe Power State 5 that consumes no more than 20 watts
Maximum Power (MP) and NVMe Power State 6 that consumes no more than 16 watts Maximum Power
(MP). Selecting DSSD Power State 18 (i.e., 18 watts Maximum Power (MP)) causes the device to enter
NVMe Power State 6 and consume no more than 16 watts Maximum Power (MP). In this example the
device reports 18 as its DSSD Power State and 6 as its NVMe Power State. Selecting NVMe Power State 6
causes the device to report 16 as its DSSD Power State and 6 as its NVMe Power State.

<!-- page 63 -->
DSSD Power State 0 does not exist, as a device that is consuming 0 watts Maximum Power (MP) is powered
off. DSSD Power States that represent a Maximum Power (MP) less than the lowest powered NVMe Power
State are invalid. The lowest numbered valid DSSD Power State is indicated in DCLP-8.

**4.8.11.1** **DSSD Power State Descriptor**

The DSSD Power State Descriptor for each DSSD Power State has the following format:

|Requirement<br>ID|Bits|Field|Field Description|
|---|---|---|---|
|DSSDPSD-1|7|Valid DSSD<br>Power State|Shall be set to 1b if the number of this DSSD Power State is greater<br>than or equal to the Minimum Valid OCP Power State (seeDCLP-8).|
|DSSDPSD-2|6:5|Reserved|Shall be cleared to zero.|
|DSSDPSD-3|4:0|NVMe Power<br>State|Shall be set to the number of the highest powered NVMe Power State<br>whose Maximum Power (MP) in watts is less than or equal to the<br>number of this DSSD Power State.|

**4.8.12 Unsupported Requirements (Log Identifier C5h)**

This log page provides a host with a consolidated report of all the Requirement IDs that the device does not
support. This log page shall be 4096 bytes with the following functional requirements and field format:

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|URLP-1|1:0|Unsupported<br>Count|2|The number of Unsupported Requirement<br>IDs.|
|URLP-2|15:2|Reserved|14|Shall be cleared to zero.|
|URLP-3|4063:16|Unsupported<br>Requirements<br>List|4048|This structure shall be populated with<br>between 0 and 253 16-byte zero padded<br>ASCII strings. Each string shall be the<br>Requirement ID of a requirement that the<br>device does not support. Entries shall be<br>in alphabetical order. Unused entries<br>shall be cleared to zero.<br>**Byte**<br>**Address**<br>**Byte Description**<br>31:16<br>First Unsupported<br>Requirement ID entry.<br>47:32<br>Second Unsupported<br>Requirement ID entry.<br>… <br>… <br>4063:4048<br>253rd Unsupported<br>Requirement ID entry.|
|URLP-4|4077:4064|Reserved|14|Shall be cleared to zero.|
|URLP-5|4079:4078|Log Page<br>Version|2|This indicates the version of the mapping<br>this log page uses. Shall be set to 0001h.|
|URLP-6|4095:4080|Log Page GUID|16|Shall be set to<br>C7BB98B7D0324863BB2C23990E9C722Fh.|

|Byte<br>Address|Byte Description|
|---|---|
|31:16|First Unsupported<br>Requirement ID entry.|
|47:32|Second Unsupported<br>Requirement ID entry.|
|…|…|
|4063:4048|253rd Unsupported<br>Requirement ID entry.|

<!-- page 64 -->
**4.8.13 Hardware Component (Log Identifier C6h)**

This log page provides the host with information regarding the hardware components on the device.  This
log page is intended to enable customers to be able to parse this log when there are component issues to be
able to find failing devices. This also enables customers to be able to parse this log for failing devices and
not require device serial numbers to find the devices with component issues.

|Requirement ID|Description|
|---|---|
|HWCOMP-1|A value of zero shall only be used if the corresponding component data is not available.|
|HWCOMP-2|Manufacturer codes shall be clearly documented and disclosed to the customer.|
|HWCOMP-3|This log shall contain the controller ASIC, PMICs, DRAM, NAND, PCB, and all other critical<br>hardware components.|
|HWCOMP-4|This log shall contain the Device Serial Number.|
|HWCOMP-5|This log shall contain the Country of Origin.|
|HWCOMP-6|This log shall contain the Global Hardware Revision.|
|HWCOMP-7|The first Component Descriptor shall start at byte 64.|
|HWCOMP-8|The last Component Descriptor shall end at the byte address which is equal to the<br>Hardware Component Log Size – 1|
|HWCOMP-9|There shall be no Dwords between two Component Descriptors.|

**4.8.13.1** **Component Descriptor**

The Hardware Component Log uses a component descriptor of the following format:

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|COMPD-1|7:0|Component<br>Date/Lot<br>Size|8|Component Date/Lot Size in Dwords.<br>This is a one-based value. A value of 0h<br>means the Component Date/Lot Code<br>field does not exist in the descriptor.  A<br>value of 1h means this field is 1 Dword<br>in size.|
|COMPD-2|15:8|Component<br>Additional<br>Information<br>Size|8|Component Additional Information Size<br>in Dwords. This is a one-based value. A<br>value of 0h means the Component<br>Additional Information field does not<br>exist in the descriptor.  A value of 1h<br>means this field is 1 Dword in size.|
|COMPD-3|19:16|Component<br>Identifier|4|This is the type of component.  This<br>shall follow the Component Identifier<br>Table.|
|COMPD-4|27:20|Component<br>Manufacture|8|The value in this field shall represent<br>Component Manufacture. If this field is<br>0h then there is no component<br>manufacture information provided.<br>This value is in hex.|

<!-- page 65 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|COMPD-5|35:28|Component<br>Revision|8|The value in this field shall represent<br>the Component Revision.  If this field is<br>0h then there is no Component Revision<br>information provided.  This value is in<br>hex.|
|COMPD-6|43:36|Component<br>Manufacture<br>Code|8|The value in this field shall represent<br>the Component Manufacture Code.  If<br>this field is 0h then there is no<br>Component Manufacture Code<br>information provided.  This value is in<br>hex.|
|COMPD-7|(Component<br>Date/Lot Size * 4)<br>+ 43:44|Component<br>Date/Lot<br>Code|Component<br>Date/Lot<br>Size * 4|The value in this field shall represent a<br>Component Date/Lot Code.  If this field<br>is 0h then there is no Component<br>Date/Lot code provided.  This value is in<br>hex.|
|COMPD-8|(Component<br>Additional<br>Information Size *<br>4) + (Component<br>Date/Lot Size * 4)<br>+ 43:Component<br>Date/Lot Size * 4)<br>+ 44|Component<br>Additional<br>Information|Component<br>Additional<br>Information<br>Size * 4|The value in this field shall represent<br>additional component information.  If<br>this field is 0h then there is no<br>additional component information.  This<br>value is in hex unless otherwise noted in<br>the component identifier.|

**4.8.13.2** **Component Identifier Table**

The following is a table of the Component Identifiers:

|Requirement<br>ID|Component<br>Identifier|Description|
|---|---|---|
|CITYPE-1|0000h|Reserved|
|CITYPE-2|0001h|This is a Controller ASIC component|
|CITYPE-3|0002h|This is a NAND Component.|
|CITYPE-4|0003h|This is a DRAM Component.|
|CITYPE-5|0004h|This is a PMIC Component.|
|CITYPE-6|0005h|This is a PCB Component|
|CITYPE-7|0006h|This is a capacitor component.|
|CITYPE-8|0007h|This is a resistor component.|
|CITYPE-9|0008h|This is a case component.|
|CITYPE-10|0009h|Device Serial Number.  The serial number shall go into the Additional<br>Component Information field and the other fields shall be 0h, except for the<br>Component Identifier and Component Additional Information Size.|

<!-- page 66 -->
|Requirement<br>ID|Component<br>Identifier|Description|
|---|---|---|
|CITYPE-11|000Ah|Country of Origin. This is a UTF-8 string detailing the device Country of<br>Origin. The Country of Origin value shall go into the Additional Component<br>Information field and the other fields shall be 0h, except for the Component<br>Identifier and Component Additional Information Size.|
|CITYPE-12|000Bh|Global Device Hardware Revision.  The Global Device Hardware Revision<br>shall go into the Additional Component Information field and the other<br>fields shall be 0h, except for the Component Identifier and Component<br>Additional Information Size. If a new revision of hardware is introduced<br>during qualification, a new unique identifier shall be reported.|
|CITYPE-15|000Ch|Born on Date. The date on which the device was manufactured. ASCII string<br>format is MMDDYYYY. The Born-on Date shall go into the Additional<br>Component Information field and the other fields shall be 0h, except for the<br>Component Identifier and Component Additional Information Size.|
|CITYPE-13|000Dh-7FFFh|Reserved|
|CITYPE-14|8000h-FFFFh|Vendor Unique Component|

**4.8.13.3** **Hardware Component Log Page**

|Requirement<br>ID|Byte Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|HWCLOG-1|1:0|Log Page<br>Version|2|This indicates the version of the mapping<br>this log page uses.  Shall be set to 0002h.|
|HWCLOG-2|15:2|Reserved|14|Shall be cleared to zero.|
|HWCLOG-3|31:16|Log Page<br>GUID|16|Shall be set to  <br>BCB6821F30CD4ED0B76B31B99F0F57DCh.|
|HWCLOG-4|47:32|Hardware<br>Component<br>Log Size|16|This is the size of the Hardware Component<br>Log in bytes.|
|HWCLOG-5|63:48|Reserved|16|Reserved.  Shall be cleared to 0h.|
|HWCLOG-6|Hardware<br>Component Log<br>Size – 1:64|Component<br>Descriptions|Hardware<br>Component<br>Log Size – 64|This shall contain the hardware descriptors.|

**4.8.14 TCG Configuration (Log Identifier C7h)**

TCG Configuration Log shall be 512 bytes in size. This log defines the data points related to TCG Opal
Security Subsystem Class (SSC) that would be useful to collect for diagnostic purposes. These data points
give point-in-time insight into the configuration and runtime state of the device which can be used to
explain either a device or host behavior.

66

|TCG Log Behavior Type|Persistence Type|
|---|---|
|A|Persistent across TCG revert: PSID, Admin SP, Locking SP|
|B|Not persistent across TCG revert|

<!-- page 67 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Behavior<br>Type|TCG Log<br>Behavior<br>Type|
|---|---|---|---|---|---|---|
|TCGL-1|0|State|1|Bit 0: C_PIN_SID Value<br>indicates whether<br>C_PIN_SID object’s PIN<br>column value is equal to<br>MSID or not.<br>0 = MSID value<br>1 = Not MSID value<br>Bit 1: C_PIN_SID<br>Authentication Blocked<br>indicates whether<br>authentication of<br>C_PIN_SID authority is<br>blocked or not due to Block<br>SID Authentication<br>command.<br>0 = Not blocked<br>1 = Blocked<br>Bit 2: Locking Enabled<br>(feature code 0002h)<br>indicates whether<br>the Locking SP is currently<br>in ‘Manufactured-Inactive’<br>or ‘Manufactured’ state.<br>0 = Locking SP not<br>activated i.e.,<br>Manufactured-Inactive<br>state<br>1 = Locking SP activated<br>i.e., Manufactured state<br>Bit 3: Single User Mode<br>Owner indicates the<br>ownership policy for the<br>RangeStart and<br>RangeLength columns of all<br>Locking Objects in Single<br>User Mode.<br>0 = User Authority<br>1 = Admins Authority<br>All other bits shall be<br>cleared to zero.|1|N/A|

<!-- page 68 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Behavior<br>Type|TCG Log<br>Behavior<br>Type|
|---|---|---|---|---|---|---|
|TCGL-2|3:1|Reserved|3|Shall be cleared to zero.|N/A|N/A|
|TCGL-3|4|Locking SP<br>Activation<br>Count|1|Count of transitions of<br>the Locking SP from<br>‘Manufactured-Inactive’ to<br>‘Manufactured’.|2|A|
|TCGL-4|5|Tper Revert<br>Count|1|Count of successful<br>invocations of the Revert<br>method on the Admin SP<br>which causes the entire<br>Tper to revert to Original<br>Factory State.|2|A|
|TCGL-5|6|Locking SP<br>Revert Count|1|Count of successful<br>invocations of the Revert<br>method on the Locking SP<br>which causes the Locking<br>SP to transition from<br>‘Manufactured’ to<br>‘Manufactured-Inactive’.|2|A|
|TCGL-6|7|Number of<br>Locking Objects|1|The number of Locking<br>Objects supported in the<br>Locking table including the<br>Global Locking Object.  If<br>the Locking SP is inactive,<br>then this value shall be<br>cleared to zero.|1|N/A|
|TCGL-7|8|Number of<br>Single User<br>Mode Locking<br>Objects|1|The current number of<br>Locking Objects in the<br>Locking table that are in<br>Single User Mode including<br>the Global Locking<br>Object.  If the Locking SP is<br>inactive, then this value<br>shall be cleared to zero.|1|N/A|
|TCGL-8|9|Number of<br>Range<br>Provisioned<br>Locking Objects|1|The current number of<br>non-Global Locking Objects<br>with non-zero RangeLength<br>value.  If the Locking SP is<br>inactive, then this value<br>shall be cleared to zero.|1|N/A|

<!-- page 69 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Behavior<br>Type|TCG Log<br>Behavior<br>Type|
|---|---|---|---|---|---|---|
|TCGL-9|10|Number of<br>Namespace<br>Provisioned<br>Locking Objects|1|The current number of<br>non-Global Locking Objects<br>with a non-zero<br>NamespaceID value.  If<br>the Locking SP is inactive,<br>then this value shall be<br>cleared to zero.  If there<br>are more than 254 non-<br>Global Locking Objects,<br>then this field shall be set<br>to FFh, and the device shall<br>implement TCGL-23.|1|N/A|
|TCGL-10|11|Number of<br>Read Locked<br>Locking Objects|1|The current number of<br>provisioned non-Global<br>Locking Objects with<br>ReadLockEnabled set to<br>True and ReadLocked set to<br>True.  If the Locking SP is<br>inactive, then this value<br>shall be cleared to zero.|1|N/A|
|TCGL-11|12|Number of<br>Write Locked<br>Locking Objects|1|The current number of<br>provisioned non-Global<br>Locking Objects with<br>WriteLockEnabled set to<br>True and WriteLocked set<br>to True.  If the Locking SP is<br>inactive, then this value<br>shall be cleared to zero.|1|N/A|
|TCGL-12|13|Number of<br>Read Unlocked<br>Locking Objects|1|The current number of<br>provisioned non-Global<br>Locking Objects<br>with ReadLockEnabled set<br>to True and ReadLocked set<br>to False.  If the Locking<br>SP is inactive, then this<br>value shall be cleared to<br>zero.|1|N/A|

<!-- page 70 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Behavior<br>Type|TCG Log<br>Behavior<br>Type|
|---|---|---|---|---|---|---|
|TCGL-13|14|Number of<br>Write Unlocked<br>Locking Objects|1|The current number of<br>provisioned non-Global<br>Locking Objects with <br>WriteLockEnabled set to<br>True and WriteLocked set<br>to False.  If the Locking SP <br>is inactive, then this value<br>shall be cleared to zero.|1|N/A|
|TCGL-14|15|Reserved|1|Shall be cleared to zero.|N/A|N/A|
|TCGL-15|19:16|SID<br>Authentication<br>Try Count|4|The Tries value for the<br>C_PIN_SID Credential<br>Object which indicates the<br>number of failed<br>authentication attempts<br>for that object since the<br>last power cycle, successful<br>authentication or Tper<br>revert.|1|N/A|
|TCGL-16|23:20|SID<br>Authentication<br>Try Limit|4|The TryLimit value for the<br>C_PIN_SID Credential<br>Object which indicates the<br>maximum number of failed<br>authentication attempts<br>for that object.|1|N/A|
|TCGL-17|27:24|Programmatic<br>TCG Reset<br>Count|4|The count of Programmatic<br>TCG Resets received by the<br>device since the last power<br>cycle.|3|A|

<!-- page 71 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Behavior<br>Type|TCG Log<br>Behavior<br>Type|
|---|---|---|---|---|---|---|
|TCGL-18|31:28|Programmatic<br>Reset Lock<br>Count|4|The count of state<br>transitions for all<br>provisioned non-Global<br>Locking Objects in the<br>following conditions:<br>• <br>Read Lock Transition<br>when<br>ReadLockedEnable =<br>True and ReadLocked<br>transitions from False<br>to True.<br>• <br>Write Lock Transition<br>when<br>WriteLockedEnable =<br>True and WriteLocked<br>transitions from False<br>True.<br>The count shall increment<br>for both explicit and<br>implicit Programmatic<br>Resets since the last power<br>cycle.|3|A|
|TCGL-19|35:32|TCG Error<br>Count|4|The count of TCG errors<br>reported to the host.|3|A|
|TCGL-23|37:36|Number of<br>Namespace<br>Provisioned<br>Locking Objects<br>Extended|2|The current number of<br>non-Global Locking Objects<br>with a non-zero<br>NamespaceID value. If<br>the Locking SP is inactive,<br>then this value shall be<br>cleared to zero.|1|N/A|
|TCGL-20|493:38|Reserved|456|Shall be cleared to zero.|N/A|N/A|
|TCGL-21|495:494|Log Page<br>Version|2|Shall be set to 0002h.|N/A|N/A|
|TCGL-22|511:496|Log Page GUID|16|Shall be set to<br>54E02A9DFA5447C083E6E<br>07EBD244006h.|N/A|N/A|

**4.8.15 Telemetry String (Log Identifier C9h)**

The Telemetry String log page enables mapping of Statistic Identifiers, Debug Class/Event Identifiers and
Debug Class/VU Event Identifier combinations to ASCII strings.

<!-- page 72 -->
**4.8.15.1** **Telemetry String Log Page Requirements**

|Requirement ID|Description|
|---|---|
|TELSLG-1|All Statistic Identifiers contained in Data Area 1 and Data Area 2 shall be contained in this<br>log page.|
|TELSLG-2|String Identifier Table entries shall be in numeric order such that the smallest Vendor<br>Unique Statistic Identifier is at the lowest address.|
|TELSLG-3|All Debug Event Class/ Event Identifier combinations contained in Telemetry Data Area 1<br>and Telemetry Data Area 2 shall be contained in this log page.|
|TELSLG-4|All Debug Event Class/ VU Event Identifier combinations contained in Telemetry Data Area<br>1 and Telemetry Data Area 2 shall be contained in this log page.|
|TELSLG-5|String Event Table entries shall be in numeric order such that the smallest Debug event<br>Class is at the lowest address.|
|TELSLG-6|String VU Event Table entries shall be in numeric order such that the smallest Debug event<br>Class is at the lowest address.|
|TELSLG-7|String Event Table entries shall be in numeric order such that for a single Debug/Event<br>Identifier combination the smallest Event Identifier is at the lowest address.|
|TELSLG-8|String VU Event Table entries shall be in numeric order such that for a single Debug/VU<br>Event Identifier combination the smallest VU Event Identifier is at the lowest address.|
|TELSLG-9|In the ASCII table (SeeSection 4.8.15.2 Telemetry String Log Page Format), characters<br>which are not valid (beyond the length of the ASCII length) shall be set to <space> (i.e.,<br>20h).|
|TELSLG-10|The String Identifier Table shall have no gaps between this table and the String Event<br>Table.|
|TELSLG-11|The String Event Table entry shall have no gaps between this table and the VU String Event<br>Table.|
|TELSLG-12|The VU String Event Table and the ASCII table shall have no gaps between these tables.|
|TELSLG-13|The String Identifier Table Entries, The String Event Table Entries and the String VU Event<br>Table Entries may point to the same ASCII Table Entry.|

**4.8.15.2** **Telemetry String Log Page Format**

The Telemetry String log page enables mapping data constructs in Telemetry Data Area 1 and Telemetry
Data Area 2 to ASCII strings. The size of the Telemetry String log page can be found in Telemetry Data Area
1 or in the Telemetry String log page. The following is the format of the Telemetry String log page:

|Requirement<br>ID|Byte Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELSTR-LOG-1|0|Log Page<br>Version|1|Shall be set to 01h.|
|TELSTR-LOG-2|15:1|Reserved|15|Shall be cleared to zero.|
|TELSTR-LOG-3|31:16|Log Page<br>GUID|16|Shall be set to<br>B13A83691A8F408B9EA495940057AA44h.|
|TELSTR-LOG-4|39:32|Telemetry<br>String Log<br>Page Size<br>(SLPS)|8|Shall be set to the number of Dwords in the<br>Telemetry String log page.|
|TELSTR-LOG-5|63:40|Reserved|24|Shall be cleared to zero.|

<!-- page 73 -->
|Requirement<br>ID|Byte Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELSTR-LOG-6|71:64|Statistics<br>Identifier<br>String<br>Table<br>Start<br>(SITS)|8|Shall be set to the number of Dwords from<br>byte 0 of this log page to the start of the<br>Statistics Identifier String Table. This shall<br>be set to 6Ch.|
|TELSTR-LOG-7|79:72|Statistics<br>Identifier<br>String<br>Table Size<br>(SITSZ)|8|Shall be set to the number of Dwords in the<br>Statistics Identifier String Table. If there are<br>no vendor unique defined values this shall<br>be set to 0h.|
|TELSTR-LOG-8|87:80|Event<br>String<br>Table<br>Start<br>(ESTS)|8|Shall be set to the number of Dwords from<br>byte 0 of this log page to the start of the<br>Event String Table.|
|TELSTR-LOG-9|95:88|Event<br>String<br>Table Size<br>(ESTSZ)|8|Shall be set to the number of Dwords in the<br>Event String Table.|
|TELSTR-LOG-10|103:96|VU Event<br>String<br>Table<br>Start<br>(VUETS)|8|Shall be set to the number of Dwords from<br>byte 0 of this log page to the start of the VU<br>Event String Table.|
|TELSTR-LOG-11|111:104|VU Event<br>String<br>Table Size<br>(VUESTZ)|8|Shall be set to the number of Dwords in the<br>VU Event String Table.|
|TELSTR-LOG-12|119:112|ASCII<br>Table<br>Start<br>(ASCTS)|8|This is the number of Dwords from byte 0 of<br>this log page until the ASCII Table Starts.|
|TELSTR-LOG-13|127:120|ASCII<br>Table Size<br>(ASCTSZ)|8|This is the number of Dwords in the ASCII<br>Table.|
|TELSTR-LOG-14|143:128|FIFO 1<br>ASCII<br>String|16|This is the name of FIFO 1.  If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-15|159:144|FIFO 2<br>ASCII<br>String|16|This is the name of FIFO 2.  If the FIFO has<br>no string name this shall be populated with<br>0h.|

<!-- page 74 -->
|Requirement<br>ID|Byte Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELSTR-LOG-16|175:160|FIFO 3<br>ASCII<br>String|16|This is the name of FIFO 3.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-17|191:176|FIFO 4<br>ASCII<br>String|16|This is the name of FIFO 4.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-18|207:192|FIFO 5<br>ASCII<br>String|16|This is the name of FIFO 5.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-19|223:208|FIFO 6<br>ASCII<br>String|16|This is the name of FIFO 6.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-20|239:224|FIFO 7<br>ASCII<br>String|16|This is the name of FIFO 7.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-21|255:240|FIFO 8<br>ASCII<br>String|16|This is the name of FIFO 8.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-22|271:256|FIFO 9<br>ASCII<br>String|16|This is the name of FIFO 9.   If the FFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-23|287:272|FIFO 10<br>ASCII<br>String|16|This is the name of FIFO 10.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-24|303:288|FIFO 11<br>ASCII<br>String|16|This is the name of FIFO 11.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-25|319:304|FIFO 12<br>ASCII<br>String|16|This is the name of FIFO 12.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-26|335:320|FIFO 13<br>ASCII<br>String|16|This is the name of FIFO 13.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-27|351:336|FIFO 14<br>ASCII<br>String|16|This is the name of FIFO 14.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-28|367:352|FIFO 15<br>ASCII<br>String|16|This is the name of FIFO 15.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-29|383:368|FIFO 16<br>ASCII<br>String|16|This is the name of FIFO 16.   If the FIFO has<br>no string name this shall be populated with<br>0h.|
|TELSTR-LOG-30|431:384|Reserved|48|Shall be cleared to 0h.|

<!-- page 75 -->
|Requirement<br>ID|Byte Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELSTR-LOG-31|(SITSZ *4) +<br>431:432|Statistics<br>Identifier<br>String<br>Table|SITSZ * 4|The format of the Statistics Identifier String<br>Table can be seen inSection 4.8.15.3<br>Statistics Identifier String Table Entry.|
|TELSTR-LOG-32|(ESTSZ  * 4) +<br>(SITSZ * 4) +<br>431:SITSZ * 4) +<br>432|Event<br>String<br>Table|ESTSZ * 4|The format of the Event Identifier String<br>Table can be seen inSection 4.8.15.4 Event<br>Identifier String Table Entry.|
|TELSTR-LOG-33|(VUESTZ * 4) +<br>(ESTSZ  * 4) +<br>(SITSZ * 4) +<br>431:ESTSZ  * 4) +<br>(SITSZ * 4) + 432|VU Event<br>String<br>Table|VUESTZ * 4|The format of the VU Event Identifier String<br>Table can be seen inSection 4.8.15.5 VU <br>Event Identifier String Table Entry.|
|TELSTR-LOG-34|(ASCTSZ * 4) +<br>(VUESTZ * 4) +<br>(ESTSZ  * 4) +<br>(SITSZ * 4) + 432:<br>(VUESTZ * 4) +<br>(ESTSZ  * 4) +<br>(SITSZ * 4) + 432|ASCII<br>Table|ASCTSZ * 4|The format of the ASCII table can be seen in<br>Section 4.8.15.6 ASCII String Example.|

A diagram of the Telemetry String log page format is as follows:

<!-- page 76 -->
**4.8.15.3** **Statistics Identifier String Table Entry**

The Statistic Identifier String Table enables translating from vendor unique statistic identifiers to ASCII
labels. The format of an entry for the Statistic Identifier String Table Entry is in the following table:

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|STR-ID-1|1:0|Vendor Specific<br>Statistic<br>Identifier|2|Shall be set the Vendor Unique Statistic Identifier<br>number.|
|STR-ID-2|2|Reserved|1|Shall be cleared to zero.|
|STR-ID-3|3|ASCII ID Length|1|Shall be set the number of ASCII Characters that are<br>valid.  This is a zero-based value so a value of 0h is 1<br>character.|

<!-- page 77 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|STR-ID-4|11:4|ASCII ID offset|8|Shall be set to the offset from Dword 0/Byte 0 of the<br>Start of the ASCII Table to the first character of the<br>string for this Statistic Identifier string. This value is in<br>Dwords.|
|STR-ID-5|15:12|Reserved|4|Shall be cleared to zero.|

**4.8.15.4** **Event Identifier String Table Entry**

The Event Identifier String Table enables translating from Event Identifier to ASCII labels. The format of an
entry for the Event Identifier String Table Entry is in the following table:

|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|STR-EV-1|0|Debug<br>Event Class|1|Shall be set the Debug Class.|
|STR-EV-2|2:1|Event<br>Identifier|2|Shall be set to the Event Identifier.|
|STR-EV-3|3|ASCII ID<br>Length|1|Shall be set to the number of ASCII Characters that are<br>valid. This is a zero-based value so a value of 0h is 1<br>character.|
|STR-EV-4|11:4|ASCII ID<br>offset|8|This is the offset from Dword 0/ byte 0 of the start of<br>the ASCII table to the ASCII data for this identifier. This<br>value is in Dwords.|
|STR-EV-5|15:12|Reserved|4|Shall be cleared to zero.|

**4.8.15.5** **VU Event Identifier String Table Entry**

The VU Event Identifier String Table enables translating from VU Event Identifier to ASCII labels. The
format of an entry for the VU Event Identifier String Table Entry is in the following table:

|Requirement ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|STR-VUEV-1|0|Debug Event<br>Class|1|Shall be set the Debug Class.|
|STR-VUEV-2|2:1|VU Event<br>Identifier|2|Shall be set to the VU Event Identifier|
|STR-VUEV-3|3|ASCII ID<br>Length|1|Shall be set to the number of ASCII Characters that are<br>valid. This is a zero-based value so a value of 0h is 1<br>character.|
|STR-VUEV-4|11:4|ASCII ID<br>offset|8|This is the offset from Dword 0/ byte 0 of the start of<br>the ASCII table to the ASCII data for this identifier. This<br>value is in Dwords.|
|STR-VUEV-5|15:12|Reserved|4|Shall be cleared to zero.|

**4.8.15.6** **ASCII String Example**

An ASCII ID Length/Decode example is shown in the following table:

<!-- page 78 -->
|Byte|Data Byte|ASCII<br>Character|
|---|---|---|
|400|54h|T|
|401|45h|E|
|402|53h|S|
|403|54h|T|
|404|20h|<space>|
|405|45h|E|
|406|58h|X|
|407|41h|A|
|408|4Dh|M|
|409|50h|P|
|410|4Ch|L|
|411|45h|E|
|412|21h|!|
|413|20h|<space>|
|414|20h|<space>|
|415|20h|<space>|

In this example the ASCII ID Length is 0Ch, which is 12 decimal. This is a zero-based count and thus there
are 13 characters to print. The first 13 characters shall be part of the ASCII output. Thus, the message to
print is:

“TEST EXAMPLE!”

The last three ASCII characters of <space> are not part of the ASCII output They are only used for padding
the string to the next Dword boundary. The last three ASCII characters of <space> are not part of the next
string.

### **4.9 Host and Controller Initiated Telemetry Log Pages**

The following requirements define a standardized format for Telemetry Data Area 1 and Telemetry Data
Area 2 for both Telemetry Host-Initiated log page (Log Identifier 07h) and Telemetry Controller-Initiated
log page (Log Identifier 08h).

**4.9.1 Theory of Operation**

This feature is designed to enable both customers and suppliers to have increased visibility into monitoring
and debugging devices.

**4.9.2 Data Partitioning Overview**

The data provided by the device for debugging is broken into two categories. There is data that impacts
I/O and data that does not impact I/O. The data generated by the device for monitoring and/or debugging
which does not impact I/O (performance/latency) for active commands in progress goes into Telemetry
Data Area 1. The data generated by the device for monitoring and/or debugging which impacts I/O
(performance/latency) for active commands in progress goes into Telemetry Data Area 2. The data format
in the Telemetry Host-Initiated log page and the Telemetry Controller-Initiated log page shall be the same
format. The information reported in Telemetry Host-Initiated Data Areas 1 and 2 shall be the same as

<!-- page 79 -->
Telemetry Controller-Initiated Data Areas 1 and 2. There is no requirement that the contents of Telemetry
Host-Initiated Data Areas 1 and 2 be the same as the contents of Telemetry Controller-Initiated Data Areas
1 and 2 because the contents of each log page are captured by different events, and each log page reports
current data (e.g., counts of commands processed) at the time of capture.

**4.9.3 Statistic Area**

The Statistic Area contains a group of Statistic Descriptors. The Statistic Descriptors may be counters or
other statistics where each statistic is a value with a statistic size. The attributes associated with each of
these statistics are Statistic Identifier, Behavior Type (see STD-LOG-12) and the length of the data field
associated with the Statistic Identifier.

**4.9.4 Event FIFO**

The Event FIFO is a queue that contains events that are generated. There is a total of up to 16 independent
Event FIFO queues that may be configured between Telemetry Data Area 1 and Telemetry Data Area 2. It
should be noted that the ordering relationship of events in the event FIFO is determined by the device.

**4.9.5 Existing NVMe Log Pages**

There are many existing NVMe log pages that are useful for monitoring the device. Some log pages have
been overlaid into Telemetry Data Area 1. This is done to enable all the monitoring information to be
gathered when polling Telemetry Data Area 1.

**4.9.6 Debug Structure Overview Summary**

The debug structure for Telemetry Data Area 1 and 2 can be seen in the following figure.  The order of the
Statistics and FIFOs are configurable, and both orders are acceptable.

<!-- page 80 -->
**4.9.7 Telemetry Data Requirements**

The following applies to telemetry logging as the ability to quickly debug failures is required:

|Requirement ID|Description|
|---|---|
|TEL-1|The device shall track the operational/event history and any critical parameters that can<br>be used to debug issues.|
|TEL-2|The supplier shall provide a table that categorizes the reason identifiers that are a super<br>set of the panic IDs inEREC-4.|
|TEL-3|Obsolete.  SeeSTD-LOG-23.|
|<br>TEL-4|<br>The Reason Identifier field (in the Telemetry Controller-Initiated log page and the<br>Telemetry Host-Initiated log page) shall be the most recent failure identifier and shall not<br>be cleared by a power cycle or reset.|

<!-- page 81 -->
|Requirement ID|Description|
|---|---|
|TEL-5|The following table provides the specifications for the Telemetry Controller-Initiated log<br>page and the Telemetry Host-Initiated log page Data Areas 1 and 2. Any vendor-specific<br>data required for root-cause analysis shall be included in Telemetry Data Area 3. If the<br>vendor-specific data required for root-cause analysis does not fit within Telemetry Data<br>Area 3, then the additional vendor-specific data shall be included in Telemetry Data Area 4.<br>**Telemetry**<br>**Data Area**<br>**Purpose**<br>**Profile 0**<br>**Data Area**<br>**Size**<br>**Latency Impact to IO**<br>1 <br>Periodic logging for<br>monitoring trends/problems<br>32,768 bytes<br>< 1 ms typical,<br>< 5 ms max<br>2 <br>Logging for debug items that<br>impact latency<br>- <br>Greater Telemetry Data<br>Area 1 Requirement<br>3 <br>Optional Vendor Unique<br>- <br>- <br>4 <br>Optional Vendor Unique<br>- <br>-|
|TEL-6|The device shall set the Telemetry Host-Initiated Data Area 1 Last Block field of the<br>Telemetry Host-Initiated log page (Log Identifier 07h) to 0040h as the factory default.|
|TEL-7|The device shall set the Telemetry Controller-Initiated Data Area 1 Last Block field of the<br>Telemetry Controller-Initiated log page (Log Identifier 08h) to 0040h as the factory default.|
|TEL-8|Information that is used to populate Telemetry Data Area 1 shall be updated in the<br>background at least once every ten minutes.|
|TEL-9|If the device supports an encrypted log for debug this may be contained in Telemetry Data<br>Area 3 and/or 4.|
|TEL-10|The number of Timestamp Events inserted into the Event FIFOs shall be sufficient to<br>debug.|
|TEL-11|For any issue that causes the controller to generate the Telemetry Controller-Initiated log<br>page, the complete contents of each of the Telemetry Controller-Initiated log page and<br>Telemetry Host-Initiated log page shall contain all of the debug information needed to root<br>cause the issue.|
|TEL-12|Updating the Error ID in theTELRI-1 Reason Identifier field shall cause a Telemetry Log<br>Changed event.|
|TEL-13|When the device encounters a failure/error the Error ID inTELRI-1 shall be a non-zero<br>value.|
|TEL-14|Data in Telemetry Data Area 1 and Telemetry Data Area 2 as defined in this specification<br>shall be decodable by the OCP plugin for the nvme-cli tool and shall meet the<br>requirements forSEC-22.|
|TEL-15|<br>Telemetry Data Area 1 and Telemetry Data Area 2 shall be supported per this specification.|
|TEL-16|A minimum of two Telemetry Profiles shall be supported.|
|TEL-17|Telemetry Profile 0 shall be the default profile from the factory.|
|TEL-18|Telemetry Profile 1 shall be sized for maximum debuggability.|
|TEL-19|The device shall support TP4109a to enable the host to access specific host telemetry.|

|Telemetry<br>Data Area|Purpose|Profile 0<br>Data Area<br>Size|Latency Impact to IO|
|---|---|---|---|
|1|Periodic logging for<br>monitoring trends/problems|32,768 bytes|< 1 ms typical,<br>< 5 ms max|
|2|Logging for debug items that<br>impact latency|-|Greater Telemetry Data<br>Area 1 Requirement|
|3|Optional Vendor Unique|-|-|
|4|Optional Vendor Unique|-|-|

<!-- page 82 -->
|Requirement ID|Description|
|---|---|
|TEL-20|On a firmware update the Vendor Specific Statistics Identifier, the Debug Event<br>Class/Events Identifier combinations and the Debug Class/VU Event Identifier<br>combinations shall not be re-purposed or removed from the Telemetry String log page.<br>This is to ensure on a firmware update that any existing Telemetry String log page is able<br>to be decoded correctly.|
|TEL-21|Telemetry Controller-Initiated log pages shall only be generated (Telemetry Controller-<br>Initiated Data Available transitions from 00h to 01h) for error conditions (e.g., they shall<br>not be generated periodically, or in response to Percentage Used changes, etc.).|
|TEL-22|The Telemetry Controller-Initiated log page and Telemetry Host-Initiated log page shall be<br>NVM subsystem in scope.|
|TEL-23|Statistics that are listed in the Description column in the table inSection 4.9.11 Statistic<br>Identifiers as coming from the SMART / Health Extended log page (Log Identifier C0h),<br>SMART / Health Information log page (Log Identifier 02h), or Endurance Group Information<br>log page (Log Identifier 09h) shall be implemented and shall be in Data Area 1.|
|TEL-24|For the Statistics in TEL-23, the device shall populate the Telemetry String Log with strings<br>that exactly match the text in the Statistic Specific Data Field column in the table inSection<br>4.9.11 Statistic Identifiers.|
|TEL-25|<br>For the statistics in TEL-23, in the Statistic Information Field, the Host Hint Type shall be set<br>to a value of Host Hint Type 1.  For statistics not in TEL-23, the Host Hint Type shall be set<br>to a value of No Host Hint.<br>|

**4.9.8 Telemetry Reason Identifier Format**

The format of the Reason Identifier shall be as follows:

|Requirement ID|Byte<br>Address|# of<br>Bytes|Field|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|TELRI-1|63:0|64|Error ID|The device shall set a unique Error ID defining the<br>persistent or transient error at the time of<br>log capture**.**|The device shall set a unique Error ID defining the<br>persistent or transient error at the time of<br>log capture**.**|The device shall set a unique Error ID defining the<br>persistent or transient error at the time of<br>log capture**.**|The device shall set a unique Error ID defining the<br>persistent or transient error at the time of<br>log capture**.**|
|TELRI-2|71:64|8|File ID|File name or hash of the source file where the error<br>occurred. Clear to zero if not applicable.|File name or hash of the source file where the error<br>occurred. Clear to zero if not applicable.|File name or hash of the source file where the error<br>occurred. Clear to zero if not applicable.|File name or hash of the source file where the error<br>occurred. Clear to zero if not applicable.|
|TELRI-3|73:72|2|Line Number|Line Number in the source file where the error<br>occurred. Clear to zero if not applicable.|Line Number in the source file where the error<br>occurred. Clear to zero if not applicable.|Line Number in the source file where the error<br>occurred. Clear to zero if not applicable.|Line Number in the source file where the error<br>occurred. Clear to zero if not applicable.|
|TELRI-4|74|1|Valid Flags||**Bit**|**Bit Description**||
|TELRI-4|74|1|Valid Flags||7:4|Reserved. Shall be cleared to zero.|Reserved. Shall be cleared to zero.|
|TELRI-4|74|1|Valid Flags||3|VU Reason Extension Field is valid.|VU Reason Extension Field is valid.|
|TELRI-4|74|1|Valid Flags||2|Shall be set to 1b if the Error ID is valid.<br>Shall be cleared to 0b if Error ID is not valid.|Shall be set to 1b if the Error ID is valid.<br>Shall be cleared to 0b if Error ID is not valid.|
|TELRI-4|74|1|Valid Flags||1|Shall be set to 1b if the File ID is valid. Shall<br>be cleared to 0b if File ID is not valid.|Shall be set to 1b if the File ID is valid. Shall<br>be cleared to 0b if File ID is not valid.|
|TELRI-4|74|1|Valid Flags||0|Shall be set to 1b if the Line Number is valid.<br>Shall be cleared to 0b if Line Number is not<br>valid.|Shall be set to 1b if the Line Number is valid.<br>Shall be cleared to 0b if Line Number is not<br>valid.|
|TELRI-5|95:75|21|Reserved|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|

<!-- page 83 -->
|Requirement ID|Byte<br>Address|# of<br>Bytes|Field|Field Description|
|---|---|---|---|---|
|TELRI-6|127:96|32|VU Reason<br>Extension|Vendor Unique reason code.|

**4.9.9 Debug Profiles**

There are many ways to configure Data Area 1, Data Area 2, the Statistics and Event FIFOs. Depending on
the problem being investigated different configurations of these fields may be desired. Debug profiles are
the mechanism that can address this challenge. The device will list the number of debug profiles
supported. The host may then configure the profile based on the problem being investigated.

**4.9.10 Statistic Descriptor**

The format of the Statistic Descriptor is in the following table:

|Value|Description|
|---|---|
|0000h|No Host Hint|
|0001h|Host Hint Type 1|
|0002h -<br>0003h|Reserved|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Col6|Col7|Col8|Col9|
|---|---|---|---|---|---|---|---|---|
|STATF-1|1:0|Statistic<br>Identifier|2|Shall contain the identifier that defines the data<br>format of this entry.|Shall contain the identifier that defines the data<br>format of this entry.|Shall contain the identifier that defines the data<br>format of this entry.|Shall contain the identifier that defines the data<br>format of this entry.|Shall contain the identifier that defines the data<br>format of this entry.|
|STATF-2|2|Statistic<br>Information|1||**Bit**|**Bit**|**Bit Description**||
|STATF-2|2|Statistic<br>Information|1||7:6|7:6|Reserved. Shall be cleared to zero.|Reserved. Shall be cleared to zero.|
|STATF-2|2|Statistic<br>Information|1||5:4|5:4|Host Hint Type. The decode for Host<br>Hint Type is as follows:<br>**Value**<br>**Description**<br>0000h<br>No Host Hint<br>0001h<br>Host Hint Type 1<br>0002h -<br>0003h<br>Reserved<br>This field is used for host decoding<br>information. TEL-25 describes the<br>requirements of what value shall be in<br>this field.|Host Hint Type. The decode for Host<br>Hint Type is as follows:<br>**Value**<br>**Description**<br>0000h<br>No Host Hint<br>0001h<br>Host Hint Type 1<br>0002h -<br>0003h<br>Reserved<br>This field is used for host decoding<br>information. TEL-25 describes the<br>requirements of what value shall be in<br>this field.|
|STATF-2|2|Statistic<br>Information|1||3:0|3:0|Behavior Type (seeSTD-LOG-12)|Behavior Type (seeSTD-LOG-12)|
|STATF-3|3|Namespace<br>Information|1||**Bit**|**Bit Description**|**Bit Description**||
|STATF-3|3|Namespace<br>Information|1||7|Namespace Information Valid. When set<br>to 1b the Namespace Identifier in STATF-3<br>and STATF-5 is valid. When cleared to 0b<br>the Namespace Identifier is not valid|Namespace Information Valid. When set<br>to 1b the Namespace Identifier in STATF-3<br>and STATF-5 is valid. When cleared to 0b<br>the Namespace Identifier is not valid|Namespace Information Valid. When set<br>to 1b the Namespace Identifier in STATF-3<br>and STATF-5 is valid. When cleared to 0b<br>the Namespace Identifier is not valid|
|STATF-3|3|Namespace<br>Information|1||6:0|Namespace Identifier[6:0]. When<br>Namespace Information Valid is set to 1b<br>this is the Namespace Identifier (NS<br>ID[6:0]). When Namespace Information<br>Valid is cleared to 0b this field is not valid<br>and shall be cleared to 0h.|Namespace Identifier[6:0]. When<br>Namespace Information Valid is set to 1b<br>this is the Namespace Identifier (NS<br>ID[6:0]). When Namespace Information<br>Valid is cleared to 0b this field is not valid<br>and shall be cleared to 0h.|Namespace Identifier[6:0]. When<br>Namespace Information Valid is set to 1b<br>this is the Namespace Identifier (NS<br>ID[6:0]). When Namespace Information<br>Valid is cleared to 0b this field is not valid<br>and shall be cleared to 0h.|

<!-- page 84 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|STATF-4|5:4|Statistic Data<br>Size|2|Shall contain the number of Dwords that is used<br>by the Statistic Specific Data field.  Valid values for<br>this field are 0h to FFFFh.|
|STATF-5|7:6|Namespace<br>Identifier[15:0]|2|Namespace Identifier[15:0].  When Namespace<br>Information Valid is set to 1b this is the<br>Namespace Identifier (NS ID[15:0]).  When<br>Namespace Information Valid is cleared to 0b this<br>field is not valid and shall be cleared to 0h.|
|STATF-6|(Statistic<br>Data Size<br>*4)+7:8|Statistic Specific<br>Data|Statistic<br>Data Size<br>*4|Shall contain data specific extended information<br>for this Statistic Data Entry type if this exists.|

**4.9.11 Statistic Identifiers**

The definitions of the Statistic Identifiers are in the following table. In addition to the Statistic Identifiers
required elsewhere (e.g., TEL-23), any Statistic Identifiers that provide value to the vendor in debugging
the device should be implemented.

|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-1|0000h|-|-|-|Reserved|
|STATI-2|0001h|1|1|Outstanding<br>Admin<br>Commands|Number of outstanding Admin<br>commands submitted by the<br>host which have not been<br>processed by the controller.<br>Pulled from Submission Queue<br>but not yet pushed to the<br>Completion Queue. This count<br>shall not include Asynchronous<br>Event Request (AER) commands.|
|STATI-3|0002h|1|1|Host Write<br>Bandwidth<br>|The percentage of the current<br>write bandwidth allowed to the<br>NAND backend due to host<br>writes.|
|STATI-4|0003h|1|1|GC Write<br>Bandwidth|The percentage of the current<br>write bandwidth allowed to the<br>NAND backend due to internal<br>writes. STATI-3 and STATI-4<br>shall add to 100%.|
|STATI-5|0004h|1|1|Active<br>Namespaces|Shall be the number of Active<br>Namespaces attached to the<br>primary controller.|
|STATI-6|0005h|5|2|Internal Write<br>Workload|Number of outstanding LBAs<br>corresponding to the Internal<br>Write Queue Depth (STATI-8).|

<!-- page 85 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-7|0006h|5|2|Internal Read<br>Workload|Number of outstanding LBAs<br>corresponding to the Internal<br>Read Queue Depth (STATI-9).|
|STATI-8|0007h|5|1|Internal Write<br>Queue Depth<br>|Number of outstanding Write<br>commands submitted by the<br>host which have not been<br>processed by the controller.<br>Pulled from Submission Queue<br>but not yet pushed to the<br>Completion Queue.|
|STATI-9|0008h|5|1|Internal Read<br>Queue Depth|Number of outstanding Read<br>commands submitted by the<br>host which have not been<br>processed by the controller.<br>Pulled from Submission Queue<br>but not yet pushed to the<br>Completion Queue.|
|STATI-10|0009h|5|2|Pending Trim<br>LBA Count|From a device perspective this is<br>the current number of LBAs<br>pending completion of the<br>background trim process due to<br>host Dataset Management –<br>Deallocate commands.|
|STATI-11|000Ah|4|2|Host Trim LBA<br>Request Count<br>|Number of LBAs that have been<br>requested by Dataset<br>Management – Deallocate<br>command since last Telemetry<br>Log collection. This shall not<br>include other commands that<br>result in de-allocation.|
|STATI-12|000Bh|1|1|Current NVMe<br>Power State|Currently set NVMe Power State<br>Descriptor at the time of this<br>Telemetry Log collection.|
|STATI-13|000Ch|1|1|Current DSSD<br>Power State|Currently set DSSD Power State<br>Descriptor at the time of this<br>Telemetry Log collection.|
|STATI-14|000Dh|4|2|Program Fail<br>Count|The number of program<br>operation failure events for the<br>life of the device.|
|STATI-15|000Eh|4|2|Erase Fail<br>Count|The number of erase operation<br>failure events for the life of the<br>device.|

<!-- page 86 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-16|000Fh|4|4|Read Disturb<br>Writes|Number of bytes written due to<br>read disturb relocations for the<br>life of the device.|
|STATI-17|0010h|4|4|Retention<br>Writes|Number of bytes written due to<br>retention relocation for the life<br>of the device.|
|STATI-18|0011h|4|4|Wear Leveling<br>Writes|Number of bytes written due to<br>wear leveling for the life of the<br>device.|
|STATI-19|0012h|4|2|Read Recovery<br>Writes|Number of bytes written due to<br>read recovery for the life of the<br>device.|
|STATI-20|0013h|1|2|GC Writes|Number of bytes written due to<br>garbage collection since last<br>Telemetry Log collection using<br>by reading either host-initiated<br>or controller-initiated log.|
|STATI-21|0014h|4|1|SRAM<br>Correctable<br>Count|Total number of correctable<br>errors due to device SRAM<br>single error correction over the<br>device lifetime.|
|STATI-22|0015h|4|1|DRAM<br>Correctable<br>Count|Total number of correctable<br>errors due to device DRAM<br>single error correction over the<br>life of the device.|
|STATI-23|0016h|4|1|SRAM<br>Uncorrectable<br>Count|Total number of uncorrectable<br>errors due to device SRAM<br>double error detection.|
|STATI-24|0017h|4|1|DRAM<br>Uncorrectable<br>Count|Total number of uncorrectable<br>errors due to device DRAM<br>double error detection.|
|STATI-25|0018h|4|1|Data Integrity<br>Error Count|Total number of data integrity<br>errors due to FTL metadata<br>integrity checks.|
|STATI-26|0019h|4|1|Read Retry<br>Error Count|The number of reads for the<br>device lifetime performed on<br>the flash because of error<br>correction (e.g., Read retries,<br>LDPC iterations, etc.).|

<!-- page 87 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-27|001Ah|4|1|PERST# Events<br>Count|Number of PERST# events<br>processed by the NVM<br>Subsystem for the lifetime of<br>the device. This count shall<br>only increment if the CC.EN bit is<br>set to 1b.|
|STATI-28|001Bh|4|2|Max Die Bad<br>Block|This information is based on a<br>single die which has the largest<br>number of bad blocks.<br>**Byte**<br>**Address**<br>**Byte Description**<br>0 <br>Worst Die % of<br>bad blocks, where<br>the range is from<br>0-100%.<br>1 <br>Reserved<br>3:2<br>Worst Die Raw<br>Number of bad<br>blocks<br>7:4<br>Reserved. Cleared<br>to 0h.|
|STATI-29|001Ch|4|2|Max NAND<br>Channel Bad<br>Block|This information is based on the<br>dies in a single NAND channel<br>which has the largest number of<br>bad blocks.<br>**Byte**<br>**Address**<br>**Byte Description**<br>0 <br>Worst NAND<br>Channel % of bad<br>blocks, where the<br>range is 0-100%<br>1 <br>Reserved<br>3:2<br>Worst NAND<br>Channel Number<br>of bad blocks<br>7:4<br>Reserved. Cleared<br>to 0h.|

|Byte<br>Address|Byte Description|
|---|---|
|0|Worst Die % of<br>bad blocks, where<br>the range is from<br>0-100%.|
|1|Reserved|
|3:2|Worst Die Raw<br>Number of bad<br>blocks|
|7:4|Reserved. Cleared<br>to 0h.|

|Byte<br>Address|Byte Description|
|---|---|
|0|Worst NAND<br>Channel % of bad<br>blocks, where the<br>range is 0-100%|
|1|Reserved|
|3:2|Worst NAND<br>Channel Number<br>of bad blocks|
|7:4|Reserved. Cleared<br>to 0h.|

<!-- page 88 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-30|001Dh|4|2|Minimum<br>NAND Channel<br>Bad Block|This information is based on the<br>dies in a single NAND channel<br>which has the smallest number<br>of bad blocks.<br>**Byte**<br>**Address**<br>**Byte Description**<br>0 <br>Best NAND<br>Channel % of bad<br>blocks where the<br>range is 0-100%<br>1 <br>Reserved<br>3:2<br>Best NAND<br>Channel Number<br>of bad blocks<br>7:4<br>Reserved. Cleared<br>to 0h.|
|STATI-33|001Eh|4|4|Physical<br>Media Units<br>Written|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-34|001Fh|4|4|Physical<br>Media Units<br>Read|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-35|0020h|4|2|Bad User<br>NAND Blocks|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-36|0021h|4|2|Bad System<br>NAND Blocks|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-37|0022h|4|2|XOR Recovery<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-38|0023h|4|2|Uncorrectable<br>Read Error<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-39|0024h|4|2|Soft ECC Error<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-40|0025h|4|2|End to End<br>Correction<br>Counts|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-41|0026h|4|1|System Data %<br>Used|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|

|Byte<br>Address|Byte Description|
|---|---|
|0|Best NAND<br>Channel % of bad<br>blocks where the<br>range is 0-100%|
|1|Reserved|
|3:2|Best NAND<br>Channel Number<br>of bad blocks|
|7:4|Reserved. Cleared<br>to 0h.|

<!-- page 89 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-42|0027h|4|2|Refresh<br>Counts|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-43|0028h|4|2|User Data<br>Erase Counts|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-44|0029h|4|1|Thermal<br>Throttling<br>Status and<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-45|002Ah|4|2|DSSD<br>Specification<br>Version|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-46|002Bh|4|2|PCIe<br>Correctable<br>Error Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-47|002Ch|4|1|Incomplete<br>Shutdowns|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-48|002Dh|4|1|% Free Blocks|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-49|002Eh|4|1|Capacitor<br>Health|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-50|002Fh|4|1|NVM Express<br>Base Errata<br>Version|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-51|0030h|4|1|NVM<br>Command Set<br>Errata Version|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-52|0031h|4|1|NVM Express<br>Management<br>Interface<br>Errata Version|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-53|0032h|4|2|Unaligned I/O|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-54|0033h|4|2|Security<br>Version<br>Number|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|

<!-- page 90 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-55|0034h|4|2|Total NUSE|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-56|0035h|4|1|PLP Start<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-57|0036h|4|4|Endurance<br>Estimate|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-58|0037h|4|2|PCIe Link<br>Retraining<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-59|0038h|4|2|Power State<br>Change Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-60|0039h|4|4|Lowest<br>Permitted<br>Firmware<br>Revision|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-61|003Ah|4|1|Log Page<br>Version|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-62|003Bh|4|1|Media Dies<br>Offline|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-63|003Ch|4|1|Max<br>Temperature<br>Recorded|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-64|003Dh|4|2|NAND Avg.<br>Erase Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-65|003Eh|4|2|Command<br>Timeouts|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-66|003Fh|4|2|System Area<br>Program Fail<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-67|0040h|4|2|System Area<br>Read Fail<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-68|0041h|4|2|System Area<br>Erase Fail<br>Count|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|

<!-- page 91 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-69|0042h|4|1|Max Peak<br>Power<br>Capability|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-70|0043h|4|1|Current Max<br>Average<br>Power|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-71|0044h|4|2|Lifetime<br>Power<br>Consumed|This is the value of this field in<br>the SMART / Health Extended<br>log page (Log Identifier C0h).|
|STATI-72|0045h|4|1|Panic / Assert<br>Count|The number of Panics / Asserts<br>the device has encountered<br>during its lifetime. This is a<br>saturating counter.|
|STATI-73|0046h|4|4|Device Busy<br>Time|Contains the amount of time the<br>device is busy with I/O<br>commands.<br>The device is busy when there is<br>a command outstanding to an<br>I/O Queue (specifically, a<br>command was issued via an I/O<br>Submission Queue Tail doorbell<br>write and the corresponding<br>completion queue entry has not<br>been posted yet to the<br>associated I/O Completion<br>Queue) on any NVMe controller<br>port. This value is reported in<br>minutes.|
|STATI-74|0047h|4|1|Critical <br>Warning|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-75|0048h|4|1|Composite<br>Temperature|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-76|0049h|4|1|Available<br>Spare|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-77|004Ah|4|1|Available<br>Spare<br>Threshold|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-78|004Bh|4|1|Percentage<br>Used|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|

<!-- page 92 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-79|004Ch|4|1|Endurance<br>Group Critical<br>Warning<br>Summary|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-80|004Dh|4|4|Data Units<br>Read|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-81|004Eh|4|4|Data Units<br>Written|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-82|004Fh|4|4|Host Read<br>Commands|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-83|0050h|4|4|Host Write<br>Commands|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-84|0051h|4|4|Controller<br>Busy Time|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-85|0052h|4|4|Power Cycles|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-86|0053h|4|4|Power On<br>Hours|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-87|0054h|4|4|Unsafe<br>Shutdowns|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-88|0055h|4|4|Media and<br>Data Integrity<br>Errors|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-89|0056h|4|4|Number Of<br>Error<br>Information<br>Log Entries|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-90|0057h|4|1|Warning<br>Composite<br>Temperature<br>Time|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-91|0058h|4|1|Critical<br>Composite<br>Temperature<br>Time|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|

<!-- page 93 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-92|0059h|4|1|Temperature<br>Sensor 1|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-93|005Ah|4|1|Temperature<br>Sensor 2|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-94|005Bh|4|1|Temperature<br>Sensor 3|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-95|005Ch|4|1|Temperature<br>Sensor 4|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-96|005Dh|4|1|Temperature<br>Sensor 5|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-97|005Eh|4|1|Temperature<br>Sensor 6|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-98|005Fh|4|1|Temperature<br>Sensor 7|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-99|0060h|4|1|Temperature<br>Sensor 8|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-100|0061h|4|1|Thermal<br>Management<br>Temperature<br>1 Transition<br>Count|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-101|0062h|4|1|Thermal<br>Management<br>Temperature<br>2 Transition<br>Count|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-102|0063h|4|1|Total Time For<br>Thermal<br>Management<br>Temperature<br>1|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|

<!-- page 94 -->
|Requirement<br>ID|Statistic<br>Identifier|Recommended<br>Behavior Type|# of<br>Dwords|Statistic<br>Specific Data<br>Field|Description|
|---|---|---|---|---|---|
|STATI-103|0064h|4|1|Total Time For<br>Thermal<br>Management<br>Temperature<br>2|This is the value of this field in<br>the SMART / Health Information<br>log page (Log Identifier 02h).|
|STATI-104|0065h|4|1|Endurance<br>Estimate|This is the value of this field in<br>the Endurance Group<br>Information log page (Log<br>Identifier 09h).|
|STATI-105|0066h|4|4|Data Units<br>Read|This is the value of this field in<br>the Endurance Group<br>Information log page (Log<br>Identifier 09h).|
|STATI-106|0067h|4|4|Data Units<br>Written|This is the value of this field in<br>the Endurance Group<br>Information log page (Log<br>Identifier 09h).|
|STATI-107|0068h|4|4|Media Units<br>Written|This is the value of this field in<br>the Endurance Group<br>Information log page (Log<br>Identifier 09h).|
|STATI-108|0069h|4|4|Number of<br>Error<br>Information<br>Log Entries|This is the value of this field in<br>the Endurance Group<br>Information log page (Log<br>Identifier 09h).|
|STATI-31|006Ah -<br>7FFFh|…|…|Reserved|Statistic Identifiers between<br>006Ch and 7FFFh are reserved<br>for future expansion.|
|STATI-32|8000h -<br>FFFFh|…|…|Vendor<br>Unique|Statistic Identifier’s between<br>8000h and FFFFh are vendor<br>unique.|

**4.9.12 Statistic Descriptor Location**

The Statistic Area location in Telemetry Data Area 1 can be found by using the Data Area 1 Statistic Area 1
Start and Data Area 1 Statistic Area 1 Size. This can be seen in the following Data Area 1 Statistics Figure:

<!-- page 95 -->
The Statistic Area location in Data Area 2 can be found by using the Data Area 2 Statistic Area Start and
Data Area 2 Statistic Size. This can be seen in the following Data Area 2 Statistic Figure:

<!-- page 96 -->
**4.9.13 Statistic Requirements**

|Requirement ID|Description|
|---|---|
|SDL-1|Statistic Area 1 shall not cross from Telemetry Data Area 1 to Telemetry Data Area 2.|
|SDL-2|Bytes in the Statistics Areas that are not contained in a Statistic Descriptor shall be zero.|
|SDL-3|The decode of the Statistic Identifiers shall be provided to the customer via the Telemetry<br>String log page.|

**4.9.14** **Event FIFO Requirements**

**4.9.14.1 Event Descriptor**

The Event Descriptor is used to log debug events in the Event FIFOs.

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVENTD-1|0|Debug Event<br>Class Type|1|Shall contain the corresponding Event Class<br>Type for this event.|
|EVENTD-2|2:1|Event<br>Identifier|2|Shall contain the corresponding Event ID<br>for this event.|
|EVENTD-3|3|Event Data<br>Size|1|Shall contain the number of Dwords that is<br>used by the Event Specific Data field.|
|EVENTD-4|(Event Data<br>Size * 4) + 3:4|Event Specific<br>Data|Event Data<br>Size * 4|Shall contain event specific extended<br>information for this event (if any).|

**4.9.14.2** **Event Classes**

This section defines the Event Class information that can be used to debug issues with the device.

**4.9.14.2.1** **Debug Event Class Types**

|Debug Event<br>Class Code|Description|
|---|---|
|00h|Reserved|
|01h|Timestamp Debug Class|
|02h|PCIe Debug Class|
|03h|NVMe Debug Class|
|04h|Reset Debug Class|
|05h|Boot Sequence Debug Class|
|06h|Firmware Assert Debug Class|
|07h|Temperature Debug Class|
|08h|Media Debug Class|
|09h|Media Wear Class|
|0Ah|Statistic Snapshot Class|
|0Bh|Virtual FIFO Event Class|
|7Fh-0Ch|Reserved|
|FFh-80h|Vendor Unique Class|

<!-- page 97 -->
**4.9.14.2.2** **Timestamp Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|EVC-TS-1|0|Timestamp<br>Debug Class|1|Shall be set to 01h.|Shall be set to 01h.|Shall be set to 01h.|Shall be set to 01h.|
|EVC-TS-2|2:1|Event<br>Identifier|2||**Event ID**|**Description**||
|EVC-TS-2|2:1|Event<br>Identifier|2||0000h|Host issued a Timestamp Set<br>Feature Command (Feature ID Eh)|Host issued a Timestamp Set<br>Feature Command (Feature ID Eh)|
|EVC-TS-2|2:1|Event<br>Identifier|2||0001h|Firmware initiated Timestamp<br>Snapshot|Firmware initiated Timestamp<br>Snapshot|
|EVC-TS-2|2:1|Event<br>Identifier|2||0002h|Obsolete|Obsolete|
|EVC-TS-2|2:1|Event<br>Identifier|2||0003h -<br>7FFFh|Reserved|Reserved|
|EVC-TS-2|2:1|Event<br>Identifier|2||8000h -<br>FFFFh|Vendor Unique|Vendor Unique|
|EVC-TS-3|3|Event Data<br>Size|1|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 2h.|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 2h.|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 2h.|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 2h.|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-TS-4|11:4|Timestamp|8|Timestamp value based on Event ID, in the format<br>defined in the NVM Express Base Specification.|Timestamp value based on Event ID, in the format<br>defined in the NVM Express Base Specification.|Timestamp value based on Event ID, in the format<br>defined in the NVM Express Base Specification.|Timestamp value based on Event ID, in the format<br>defined in the NVM Express Base Specification.|
|EVC-TS-5|13:12|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU Data field to be<br>decoded.|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU Data field to be<br>decoded.|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU Data field to be<br>decoded.|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU Data field to be<br>decoded.|
|EVC-TS-6|(Event Data<br>Size * 4) +<br>3:14|VU Data|(Event<br>Data Size<br>* 4) - 10|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|

**4.9.14.2.3** **PCIe Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-PCI-1|0|PCIe<br>Debug<br>Class|1|Shall be set to 02h.|

<!-- page 98 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-PCI-2|2:1|Event<br>Identifier|2|The device shall log PCIe Debug Events as follows:<br>**Event ID**<br>**Description**<br>0000h<br>Link Up.<br>0001h<br>Link Down.<br>0002h<br>PCIe Error Detected.<br>0003h<br>PERST# Asserted.<br>0004h<br>PERST# De-asserted.<br>0005h<br>Refclk Stable.<br>0006h<br>Vmain Stable.<br>0007h<br>Link Speed and Width Negotiated.<br>0008h -<br>7FFFh<br>Reserved<br>8000h -<br>FFFFh<br>Vendor Unique|
|EVC-PCI-3|3|Event<br>Data Size|1|This field indicates the number of Dwords in the Event<br>Specific Data field. If the VU Event Identifier field and VU<br>data field do not exist then, then this field shall be set to<br>1h.|

98

|Event ID|Description|
|---|---|
|0000h|Link Up.|
|0001h|Link Down.|
|0002h|PCIe Error Detected.|
|0003h|PERST# Asserted.|
|0004h|PERST# De-asserted.|
|0005h|Refclk Stable.|
|0006h|Vmain Stable.|
|0007h|Link Speed and Width Negotiated.|
|0008h -<br>7FFFh|Reserved|
|8000h -<br>FFFFh|Vendor Unique|

<!-- page 99 -->
|Byte<br>Address|Byte Description|
|---|---|
|4|State changed flags:<br>● 00h = Unchanged<br>● 01h = Link Speed Changed<br>● 02h = Link Width Changed<br>● 03h - FFh = Reserved|
|5|Link Speed:<br>● 00h = Reserved<br>● 01h = PCIe Gen1<br>● 02h = PCIe Gen2<br>● 03h = PCIe Gen3<br>● 04h = PCIe Gen4<br>● 05h = PCIe Gen5<br>● 06h = PCIe Gen6<br>● 07h = PCIe Gen7<br>● 08h - FFh = Reserved|
|6|Link Width:<br>● 00h = Reserved<br>● 01h = x1<br>● 02h = x2<br>● 03h = x4<br>● 04h = x8<br>● 05h = x16<br>● 06h - FFh = Reserved|
|7|Reserved.  Shall be cleared to zero.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-PCI-4|7:4|PCIe<br>Debug<br>Event<br>Data|4|For PCIe Debug Event ID 7, the device shall log the<br>negotiated Link Speed and Width as follows:<br>**Byte**<br>**Address**<br>**Byte Description**<br>4 <br>State changed flags:<br>● 00h = Unchanged<br>● 01h = Link Speed Changed<br>● 02h = Link Width Changed<br>● 03h - FFh = Reserved<br>5 <br>Link Speed:<br>● 00h = Reserved<br>● 01h = PCIe Gen1<br>● 02h = PCIe Gen2<br>● 03h = PCIe Gen3<br>● 04h = PCIe Gen4<br>● 05h = PCIe Gen5<br>● 06h = PCIe Gen6<br>● 07h = PCIe Gen7<br>● 08h - FFh = Reserved<br>6 <br>Link Width:<br>● 00h = Reserved<br>● 01h = x1<br>● 02h = x2<br>● 03h = x4<br>● 04h = x8<br>● 05h = x16<br>● 06h - FFh = Reserved<br>7 <br>Reserved.  Shall be cleared to zero.<br>For all other PCIe Debug Event IDs, this field shall be<br>cleared to zero.|
|EVC-PCI-5|9:8|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event Identifier<br>that enables the VU data to be decoded.|
|EVC-PCI-6|(Event<br>Data Size<br>* 4) + 3:10|VU Data|(Event<br>Data<br>Size *<br>4) – 6|Vendor Unique Data.  The size of this data is determined<br>based on the Event Data Size if this field exists.|

<!-- page 100 -->
**4.9.14.2.4** **NVMe Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-NVME-1|0|NVMe<br>Debug<br>Class|1|Shall be set to 03h.|
|EVC-NVME-2|2:1|Event<br>Identifier|2|The device shall log NVMe Debug Events as follows:<br>**Event**<br>**ID**<br>**Description**<br>0000h<br>CC.EN transitions from 0b to 1b.<br>0001h<br>CC.EN transitions from 1b to 0b.<br>0002h<br>CSTS.RDY transitions from 0b to 1b.<br>0003h<br>CSTS.RDY transitions from 1b to 0b.<br>0004h<br>Reserved<br>0005h<br>Create I/O Submission Queue Command or Create<br>I/O Completion Queue Command Processed.<br>0006h<br>In-band Admin Command Processed other than<br>Create I/O Submission Queue Command or Create<br>I/O Completion Queue Command Processed.<br>0007h<br>An Admin command returned a non-zero Status<br>Code.<br>0008h<br>An I/O Command Returned a Non-zero Status<br>Code.<br>0009h<br>CSTS.CFS transitioned from 0b to 1b<br>000Ah<br>Admin Submission Queue Base Address Written<br>(AQA) or Admin Completion Queue Based Address<br>(ACQ) written.<br>000Bh<br>Controller Configuration Register (CC) Changed<br>except for the cases that are covered in 0000h and<br>0001h.<br>000ChController Status Register (CSTS) Changed except<br>for the cases that are covered in 0002h and 0003h.<br>000DhDelete I/O Completion Queue Command or Delete<br>I/O Submission Queue Command Processed.<br>000Eh<br>Out of-band Command Processed.<br>000Fh<br>Out-of-band Asynchronous Event Message<br>Transmitted.<br>0010h<br>Panic AEN was sent (seeEREC-5).<br>0011h<br>- <br>7FFFh<br>Reserved<br>8000h<br>-<br>FFFFh<br>Vendor Unique|

|Event<br>ID|Description|
|---|---|
|0000h|CC.EN transitions from 0b to 1b.|
|0001h|CC.EN transitions from 1b to 0b.|
|0002h|CSTS.RDY transitions from 0b to 1b.|
|0003h|CSTS.RDY transitions from 1b to 0b.|
|0004h|Reserved|
|0005h|Create I/O Submission Queue Command or Create<br>I/O Completion Queue Command Processed.|
|0006h|In-band Admin Command Processed other than<br>Create I/O Submission Queue Command or Create<br>I/O Completion Queue Command Processed.|
|0007h|An Admin command returned a non-zero Status<br>Code.|
|0008h|An I/O Command Returned a Non-zero Status<br>Code.|
|0009h|CSTS.CFS transitioned from 0b to 1b|
|000Ah|Admin Submission Queue Base Address Written<br>(AQA) or Admin Completion Queue Based Address<br>(ACQ) written.|
|000Bh|Controller Configuration Register (CC) Changed<br>except for the cases that are covered in 0000h and<br>0001h.|
|000Ch|Controller Status Register (CSTS) Changed except<br>for the cases that are covered in 0002h and 0003h.|
|000Dh|Delete I/O Completion Queue Command or Delete<br>I/O Submission Queue Command Processed.|
|000Eh|Out of-band Command Processed.|
|000Fh|Out-of-band Asynchronous Event Message<br>Transmitted.|
|0010h|Panic AEN was sent (seeEREC-5).|
|<br>0011h<br>- <br>7FFFh|<br>Reserved|
|8000h<br>-<br>FFFFh|Vendor Unique|

<!-- page 101 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-NVME-3|3|Event<br>Data Size|1|This field indicates the number of Dwords in the Event Specific<br>Data field. If the VU Event Identifier field and VU data field do<br>not exist then, then this field shall be set to 2h.|

<!-- page 102 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|

<!-- page 103 -->
|Byte<br>Address|Byte Description|
|---|---|
|4|Command Opcode|
|6:5|The value of the Status field from CQEDW0 is<br>stored in bits 14:0 of this field and bit 15 of this<br>field shall be cleared to 0b.|
|8:7|Command Identifier (CID)|
|10:9|Submission Queue Identifier (SQID)|
|11|For Get Log Page, this field shall indicate the Log<br>Page Identifier.<br>For Get Features and Set Features, this field shall<br>indicate the Feature Identifier.<br>For NVMe-MI Send and NVMe-MI Receive, this<br>field shall indicate the NVMe-MI Command<br>Opcode.<br>For all other commands, this field is reserved and<br>shall be cleared to 0h.|

|Byte Address|Byte Description|
|---|---|
|7:4|Controller Configuration Register|
|11:8|Reserved. Shall be cleared to 0h.|

|Byte Address|Byte Description|
|---|---|
|7:4|Controller Status Register|
|11:8|Reserved. Shall be cleared to 0h.|

|Byte Address|Byte Description|
|---|---|
|4|Command Opcode|
|6:5|For Admin Commands, the value of the<br>Status field from CQEDW0 is stored in<br>bits 14:0 of this field and bit 15 of this<br>field shall be cleared to 0b.<br> <br>Cleared to 0h for all other commands.|
|7|NVMe-MI Status Code|

<!-- page 104 -->
|8|Byte 1 from the Request Message|
|---|---|
|9|Byte 2 from the Request Message|
|11:10|Reserved.  Shall be cleared to 0h.|

|Byte Address|Byte Description|
|---|---|
|11:4|Asynchronous Event Identifiers in the<br>AEM for up to 8 Asynchronous Events<br>where the first event that occurred is at<br>offset 4, the second event that occurred<br>is at offset 5, etc.  If there are less than 8<br>AEs in the AEM, then unused bytes shall<br>be cleared to 0h.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|||||8 <br>Byte 1 from the Request Message<br>9 <br>Byte 2 from the Request Message<br>11:10<br>Reserved.  Shall be cleared to 0h.<br>For NVMe Debug Event ID 0Fh the device shall log the NVMe<br>Debug Event Data as follows:<br>**Byte Address**<br>**Byte Description**<br>11:4<br>Asynchronous Event Identifiers in the<br>AEM for up to 8 Asynchronous Events<br>where the first event that occurred is at<br>offset 4, the second event that occurred<br>is at offset 5, etc.  If there are less than 8<br>AEs in the AEM, then unused bytes shall<br>be cleared to 0h.<br>For all other NVMe Debug Event IDs, this field shall be cleared<br>to zero.|
|EVC-NVME-5|13:12|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event Identifier that<br>enables the VU data to be decoded.|
|EVC-NVME-6|(Event<br>Data<br>Size *<br>4) +<br>3:14|VU Data|(Event<br>Data<br>Size *<br>4) –<br>10|Vendor Unique Data.  The size of this data is determined based<br>on the Event Data Size if this field exists.|

**4.9.14.2.5** **Reset Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-RST-1|0|Reset<br>Debug<br>Class|1|Shall be set to 04h.|
|EVC-RST-2|2:1|Event<br>Identifier|2|The device shall log Reset Debug Events as follows:<br>**Event ID**<br>**Description**<br>0000h<br>PCIe Conventional Hot Reset.<br>0001h<br>Main Power Cycle.<br>0002h<br>PERST#.<br>0003h<br>PCIe Function Level Reset.<br>0004h<br>NVM Subsystem Reset.<br>0005h -<br>7FFFh<br>Reserved<br>8000h -FFFFh<br>Vendor Unique|

|Event ID|Description|
|---|---|
|0000h|PCIe Conventional Hot Reset.|
|0001h|Main Power Cycle.|
|0002h|PERST#.|
|0003h|PCIe Function Level Reset.|
|0004h|NVM Subsystem Reset.|
|0005h -<br>7FFFh|Reserved|
|8000h -FFFFh|Vendor Unique|

<!-- page 105 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-RST-3|3|Event Data<br>Size|1|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 0h.<br>|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-RST-4|5:4|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU data to be decoded.|
|EVC-RST-5|(Event Data<br>Size * 4) +<br>3:6|VU Data|(Event<br>Data Size<br>* 4) – 2|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this field<br>exists.|

**4.9.14.2.6** **Boot Sequence Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-BS-1|0|Boot<br>Sequence<br>Debug<br>Class|1|Shall be set to 05h.|

<!-- page 106 -->
|Event<br>ID|Description|
|---|---|
|0000h|Main Firmware Boot Complete.  For a single<br>controller subsystem, this is when all boot<br>activities required to allow I/O commands<br>to be processed are completed excluding<br>the enablement of the controller.  This is<br>always after the FTL load from NVM<br>Complete, FTL Rebuild Started and FTL<br>Rebuild Completes events.|
|0001h|FTL Load from NVM Complete.  This means<br>the SSD downloaded the entire FTL table<br>from NVM to internal memory (i.e., no<br>journaling data is required to be loaded).|
|0002h|FTL Rebuild Started.  This is after FTL Load<br>from NVM has completed, if the FTL table is<br>required to be rebuilt from journaling data,<br>then mark the start.|
|0003h|FTL Rebuild Complete.  This means the FTL<br>table is ready to fully support I/O<br>commands.|
|0004h<br>-7FFFh|Reserved|
|8000h<br>-FFFFh|Vendor Unique|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-BS-2|2:1|Event ID|2|The device shall log Boot Sequence Debug Events as<br>follows:<br>**Event**<br>**ID**<br>**Description**<br>0000h<br>Main Firmware Boot Complete.  For a single<br>controller subsystem, this is when all boot<br>activities required to allow I/O commands<br>to be processed are completed excluding<br>the enablement of the controller.  This is<br>always after the FTL load from NVM<br>Complete, FTL Rebuild Started and FTL<br>Rebuild Completes events.<br>0001h<br>FTL Load from NVM Complete.  This means<br>the SSD downloaded the entire FTL table<br>from NVM to internal memory (i.e., no<br>journaling data is required to be loaded).<br>0002h<br>FTL Rebuild Started.  This is after FTL Load<br>from NVM has completed, if the FTL table is<br>required to be rebuilt from journaling data,<br>then mark the start.<br>0003h<br>FTL Rebuild Complete.  This means the FTL<br>table is ready to fully support I/O<br>commands.<br>0004h<br>-7FFFh<br>Reserved<br>8000h<br>-FFFFh<br>Vendor Unique|
|EVC-BS-3|3|Event Data<br>Size|1|This field indicates the number of Dwords in the Event<br>Specific Data field.  If the VU Event Identifier field and<br>VU data field do not exist then, then this field shall be<br>set to 0h.|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-BS-4|5:4|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event Identifier<br>that enables the VU data to be decoded.|
|EVC-BS-5|(Event<br>Data Size<br>* 4) +3:6|VU Data|(Event<br>Data<br>Size * 4)<br>– 2|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this field<br>exists.|

<!-- page 107 -->
**4.9.14.2.7** **Firmware Assert Debug Event Class Format**

|Event ID|Description|
|---|---|
|0000h|Assert in NVMe Processing Code.|
|0001h|Assert in Media Code.|
|0002h|Assert in Security Code.|
|0003h|Assert in Background Services Code.|
|0004h|FTL Rebuild Failed.|
|0005h|FTL Data Mismatch.|
|0006h|Assert in Other Code.|
|0007h -<br>7FFFh|Reserved|
|8000h -FFFFh|Vendor Unique|

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-ASRT-1|0|Firmware<br>Assert Debug<br>Class|1|Shall be set to 06h.|
|EVC-ASRT-2|2:1|Event<br>Identifier|2|The device shall log Firmware Assert Debug Events as<br>follows:<br>**Event ID**<br>**Description**<br>0000h<br>Assert in NVMe Processing Code.<br>0001h<br>Assert in Media Code.<br>0002h<br>Assert in Security Code.<br>0003h<br>Assert in Background Services Code.<br>0004h<br>FTL Rebuild Failed.<br>0005h<br>FTL Data Mismatch.<br>0006h<br>Assert in Other Code.<br>0007h -<br>7FFFh<br>Reserved<br>8000h -FFFFh Vendor Unique|
|EVC-ASRT-3|3|Event Data<br>Size|1|This field indicates the number of Dwords in the Event<br>Specific Data field.  If the VU Event Identifier field and<br>VU data field do not exist then, then this field shall be<br>set to 0h.|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-ASRT-4|5:4|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event Identifier<br>that enables the VU data to be decoded.|
|EVC-ASRT-5|(Event Data<br>Size * 4)<br>+3:6|VU Data|(Event<br>Data Size<br>* 4) – 2|Vendor Unique Data.  The size of this data is determined<br>based on the Event Data Size if this field exists.|

**4.9.14.2.8** **Temperature Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-TEMP-1|0|Temperature<br>Debug Class|1|Shall be set to 07h.|

<!-- page 108 -->
|Event ID|Description|
|---|---|
|0000h|Composite Temperature<br>decreases to (WCTEMP – 2)|
|0001h|Composite Temperature<br>increases to WCTEMP|
|0002h|Composite Temperature<br>increases to reach CCTEMP.|
|0003h -<br>7FFFh|Reserved|
|8000h -<br>FFFFh|Vendor Unique|

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-TEMP-2|2:1|Event Identifier|2|The device shall log Temperature Debug Events<br>as follows:<br>**Event ID**<br>**Description**<br>0000h<br>Composite Temperature<br>decreases to (WCTEMP – 2)<br>0001h<br>Composite Temperature<br>increases to WCTEMP<br>0002h<br>Composite Temperature<br>increases to reach CCTEMP.<br>0003h -<br>7FFFh<br>Reserved<br>8000h -<br>FFFFh<br>Vendor Unique<br>Once the event is logged 2 degrees of hysteresis<br>should be applied to avoid additional entries<br>being generated.|
|EVC-TEMP-3|3|Event Data Size|1|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event<br>Identifier field and VU data field do not exist<br>then, then this field shall be set to 0h.<br>|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-TEMP-4|5:4|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU data to be<br>decoded.|
|EVC-TEMP-5|(Event Data<br>Size * 4)<br>+3:6|VU Data|(Event<br>Data Size<br>* 4) – 2|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|

**4.9.14.2.9** **Media Debug Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-MEDIA-1|0|Media<br>Debug<br>Class|1|Shall be set to 08h.|

<!-- page 109 -->
|Event ID|Description|
|---|---|
|0000h|XOR (or equivalent) Recovery<br>Invoked.|
|0001h|Uncorrectable Media Error|
|0002h|Block Marked Bad Due to Program<br>Error.|
|0003h|Block Marked Bad Due to Erase<br>Error.|
|0004h|Block Marked Bad Due to Read<br>Error.|
|0005h|Plane Failure Event.|
|0006h -<br>7FFFh|Reserved|
|8000h -<br>FFFFh|Vendor Unique|

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-MEDIA-2|2:1|Event<br>Identifier|2|The device shall log Media Debug Events as follows:<br>**Event ID**<br>**Description**<br>0000h<br>XOR (or equivalent) Recovery<br>Invoked.<br>0001h<br>Uncorrectable Media Error<br>0002h<br>Block Marked Bad Due to Program<br>Error.<br>0003h<br>Block Marked Bad Due to Erase<br>Error.<br>0004h<br>Block Marked Bad Due to Read<br>Error.<br>0005h<br>Plane Failure Event.<br>0006h -<br>7FFFh<br>Reserved<br>8000h -<br>FFFFh<br>Vendor Unique|
|EVC-MEDIA-3|3|Event Data<br>Size|1|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 0h.|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-MEDIA-4|5:4|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU data to be decoded.|
|EVC-MEDIA-5|(Event Data<br>Size * 4) +<br>3:6|VU Data|(Event<br>Data Size<br>* 4) – 2|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|

**4.9.14.2.10** **Media Wear Event Class Format**

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-WEAR-1|0|Media<br>Wear Class|1|Shall be set to 09h.  This event shall be logged<br>once every 24 hours.|
|EVC-WEAR-2|2:1|Event<br>Identifier|2|The device shall log Wear Debug Events as follows:<br>**Event ID**<br>**Description**<br>0000h<br>Media Wear<br>0001h - 7FFFh<br>Reserved<br>8000h-FFFFh<br>Vendor Unique|

|Event ID|Description|
|---|---|
|0000h|Media Wear|
|0001h - 7FFFh|Reserved|
|8000h-FFFFh|Vendor Unique|

<!-- page 110 -->
|Byte Address|Description|
|---|---|
|7:4|Host Terabytes Written.|
|11:8|Media Terabytes Written.|
|15:12|Media Terabytes Erased.|

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-WEAR-3|3|Event Data<br>Size|1|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Event Identifier<br>field and VU data field do not exist then, then this<br>field shall be set to 3h.<br>|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-WEAR-4|15:4|Current<br>Media<br>Wear|12|For Wear Debug Event ID 00h, the device shall log<br>the current wear as follows:<br>**Byte Address**<br>**Description**<br>7:4<br>Host Terabytes Written.<br>11:8<br>Media Terabytes Written.<br>15:12<br>Media Terabytes Erased.<br>For all other Wear Event IDs, this field shall be<br>cleared to zero.|
|EVC-WEAR-4|17:16|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The VU Event<br>Identifier that enables the VU data to be decoded.|
|EVC-WEAR-5|(Event Data<br>Size * 4) +<br>3:18|VU Data|(Event<br>Data Size<br>* 4) – 14|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|

**4.9.14.2.11** **Statistic Snapshot Class**

For the Statistic Snapshot Class. This enables the device to take a snapshot of a statistic descriptor and
store this value in the Event FIFO.

|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-SNP-1|0|Statistic Snapshot<br>Class|1|Shall be set to 0Ah.  This is a<br>statistic snapshot of a statistics<br>descriptor.|
|EVC-SNP-2|3:1|Reserved|3|Reserved.  Cleared to 0h.|
|EVC-SNP-3|5:4|Statistic Identifier|2|This field shall contain the<br>value inSTATF-1.|
|EVC-SNP-4|6|Statistic Information|1|<br>This field shall contain the<br>value inSTATF-2. <br> <br> <br>|
|EVC-SNP-5|7|Namespace<br>Information|1|This field shall contain the<br>value inSTATF-3. <br>|

<!-- page 111 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-SNP-6|9:8|Statistic Data Size|2|This field shall contain the<br>value inSTATF-4.|
|EVC-SNP-7|11:10|Namespace<br>Identifier[15:0]|2|This field shall contain the<br>value inSTATF-5.|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-SNP-8|(Statistic Data Size<br>* 4) + 11:12|Statistic Specific<br>Data|Statistic Data<br>Size * 4|This field shall contain the<br>value inSTATF-6.|

**4.9.14.2.12** **Virtual FIFO Event Class Format**

For the Virtual FIFO Class the format of the data is:

|Event ID|Description|
|---|---|
|0000h|Virtual FIFO Start|
|0001h|Virtual FIFO End|
|0002-FFFFh|Reserved|

|Bit|VU Virtual FIFO Identifier Bit<br>Description|
|---|---|
|15:11|This is the physical Event FIFO Number.<br>Valid values are 1h to 10h.   A value of<br>0h is not valid.  An example physical<br>event FIFO is TELDF-18 is event FIFO 1.|
|10:0|This is the virtual FIFO number within<br>the physical FIFO.<br>Note:   Bits 7:0 are the LSB which is in<br>byte 4.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|EVC-VF-1|0|Virtual FIFO<br>Class|1|Shall be set to 0Bh.|
|EVC-VF-2|2:1|Virtual FIFO<br>Identifier|2|Virtual FIFO Event Identifier:<br>**Event ID**<br>**Description**<br>0000h<br>Virtual FIFO Start<br>0001h<br>Virtual FIFO End<br>0002-FFFFh<br>Reserved|
|EVC-VF-3|3|Virtual FIFO<br>Data Size|1|This shall be set to 1h.|
|EVC-VF-4|5:4|VU Virtual<br>FIFO<br>Identifier|2|This is the required format of the VU Virtual FIFO Identifier.<br>**Bit**<br>**VU Virtual FIFO Identifier Bit**<br>**Description**<br>15:11<br>This is the physical Event FIFO Number.<br>Valid values are 1h to 10h.   A value of<br>0h is not valid.  An example physical<br>event FIFO is TELDF-18 is event FIFO 1.<br>10:0<br>This is the virtual FIFO number within<br>the physical FIFO.<br>Note:   Bits 7:0 are the LSB which is in<br>byte 4.|
|EVC-VF-5|7:6|Reserved|2|This shall be set to 0h.|

This indicates the start/end of a virtual FIFO within a physical FIFO.  The name of the virtual FIFO can be
found in the String Log using the VU Virtual FIFO Identifier.

**4.9.14.2.13** **Vendor Unique Event Class Format**

For the Vendor Unique debug class.

<!-- page 112 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|EVC-VU-1|0|Debug VU<br>Class|1|Shall be set to a value in the range 80h to FFh.|
|EVC-VU-2|2:1|VU Event<br>Identifier|2|Vendor Unique Event Identifier.  The Vendor<br>Unique event identifiers under the debug VU<br>Class shall be in the range 0h to FFFFh.|
|EVC-VU-3|3|VU Event<br>Data Size|1|This field indicates the number of Dwords in the<br>Event Specific Data field.  If the VU Specific Data<br>field does not exist then, then this field shall be<br>set to 0h.<br>Valid values for this field are 0 to FF.<br>|
|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|**Event Specific Data**|
|EVC-VU-4|(VU vent Data<br>Size * 4) + 3:4|VU Data|VU Event<br>Data Size *<br>4|Vendor Unique Data.  The size of this data is<br>determined based on the Event Data Size if this<br>field exists.|

**4.9.15 Event FIFO Location**

The Event FIFO X location in Telemetry Data Area 1 can be found by using the Event FIFO X Start, Event
FIFO X Size. This can be seen in the following Telemetry Data Area 1 Event FIFO Figure:

The Event FIFO location in Telemetry Data Area 2 can be found by using the Event FIFO X Start, Event FIFO
X Data End. This can be seen in the following Telemetry Data Area 2 Event FIFO Figure:

<!-- page 113 -->
**4.9.15.1** **Event FIFO Requirements**

|Requirement ID|Description|
|---|---|
|EVF-1|The oldest event descriptor shall be at the Event FIFO Start Address.|
|EVF-2|There shall be no gaps between the data in one descriptor and the next descriptor.|
|EVF-3|The event FIFO shall only have complete descriptors (i.e., no partial descriptors).|
|EVF-4|All data contained in the event FIFO that is not contained in an event descriptor shall be<br>cleared to zero.|
|EVF-5|For a single FIFO, the Event FIFO Start and Event FIFO End shall be in the same Telemetry<br>Data Area.|
|EVF-6|Event FIFO Start and End locations shall not overlap with the Statistic Descriptor locations.|
|EVF-7|The decode of the Event Class and Vendor Unique Event Class shall be provided to the<br>customer via the Telemetry String log page.|

**4.9.16** **Telemetry Data Area**

**4.9.16.1 Telemetry Data Format**

Telemetry Data Area 1 has the following format. It should be noted that this is the format of Telemetry
Data Area 1 in the Telemetry log, which does not start from byte 0/Dword 0.

<!-- page 114 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELDF-1|1:0|Major<br>Version|2|This field shall be set to 0003h. A change of the<br>Major Version number indicates that the changes<br>to the Telemetry Data Area format decode are not<br>host software backward compatible.|
|TELDF-2|3:2|Minor<br>Version|2|This field shall be set to 0001h. A change of the<br>Minor Version number indicates that the changes<br>to the Telemetry Data Area format decode are<br>host software backward compatible.|
|TELDF-3|7:4|Reserved|4|Shall be cleared to zero.|
|TELDF-4|15:8|Timestamp|8|Shall be set to the Timestamp when the Telemetry<br>Log (Host Initiated or Controller Initiated) Get Log<br>command was received by the device. The format<br>of this field shall be as defined in Timestamp<br>(Feature Identifier 0Eh) of the NVM Express Base<br>Specification.|
|TELDF-5|31:16|Log Page<br>GUID|16|This field shall be set<br>to BA560A9C3043424CBC73719D87E64EFAh.|
|TELDF-6|32|Number<br>Telemetry<br>Profiles<br>Supported|1|Shall be set to the number of Telemetry Profiles<br>supported by the device.|
|TELDF-7|33|Telemetry<br>Profile<br>Selected<br>(TPS)|1|Shall be set to the currently selected Telemetry<br>Profile number.|
|TELDF-8|39:34|Reserved|6|Shall be cleared to zero.|
|TELDF-9|47:40|Telemetry<br>String Log<br>Page Size<br>(SLPS)|8|Shall be set to the number of Dwords in the<br>Telemetry String log page.|
|TELDF-10|55:48|Reserved|8|Shall be cleared to zero.|
|TELDF-11|63:56|Firmware<br>Revision|8|Shall be set to the value of the Firmware Revision<br>field in the Identify Controller data structure.|
|TELDF-12|95:64|Reserved|32|Shall be cleared to zero.|
|TELDF-13|103:96|Data Area 1<br>Statistic<br>Start|8|This field shall contain the Dword offset of the<br>start of the Statistic Buffer in Telemetry Data Area<br>1. This offset starts from Dword 0 / byte 0 in<br>Telemetry Data Area 1. This field shall contain a<br>zero-based value.|
|TELDF-14|111:104|Data Area 1<br>Statistic<br>Size|8|This field shall contain the size of the Statistic<br>Buffer in Data Area 1 in Dwords. If there are no<br>Statistic Descriptors a value of 0h shall be<br>reported.|

<!-- page 115 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|TELDF-15|119:112|Data Area 2<br>Statistic<br>Start|8|This field shall contain the Dword offset of the<br>start of the Statistic Buffer in Telemetry Data Area<br>2.  This offset starts from Dword 0 / byte 0 in<br>Telemetry Data Area 2.  This field shall contain a<br>zero-based value.|This field shall contain the Dword offset of the<br>start of the Statistic Buffer in Telemetry Data Area<br>2.  This offset starts from Dword 0 / byte 0 in<br>Telemetry Data Area 2.  This field shall contain a<br>zero-based value.|This field shall contain the Dword offset of the<br>start of the Statistic Buffer in Telemetry Data Area<br>2.  This offset starts from Dword 0 / byte 0 in<br>Telemetry Data Area 2.  This field shall contain a<br>zero-based value.|This field shall contain the Dword offset of the<br>start of the Statistic Buffer in Telemetry Data Area<br>2.  This offset starts from Dword 0 / byte 0 in<br>Telemetry Data Area 2.  This field shall contain a<br>zero-based value.|
|TELDF-16|127:120|Data Area 2<br>Statistic<br>Size|8|This field shall contain the size of the Statistic<br>Buffer in Data Area 2 in Dwords.  If there are no<br>Statistic Descriptors a value of 0h shall be<br>reported.|This field shall contain the size of the Statistic<br>Buffer in Data Area 2 in Dwords.  If there are no<br>Statistic Descriptors a value of 0h shall be<br>reported.|This field shall contain the size of the Statistic<br>Buffer in Data Area 2 in Dwords.  If there are no<br>Statistic Descriptors a value of 0h shall be<br>reported.|This field shall contain the size of the Statistic<br>Buffer in Data Area 2 in Dwords.  If there are no<br>Statistic Descriptors a value of 0h shall be<br>reported.|
|TELDF-17|159:128|Reserved|32|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|
|TELDF-18|160|Event FIFO<br>1 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-18|160|Event FIFO<br>1 Data Area|1||00h|Event FIFO 1 does not exist|Event FIFO 1 does not exist|
|TELDF-18|160|Event FIFO<br>1 Data Area|1||01h|Event FIFO 1 exists in<br>Telemetry Data Area 1|Event FIFO 1 exists in<br>Telemetry Data Area 1|
|TELDF-18|160|Event FIFO<br>1 Data Area|1||02h|Event FIFO 1 exists in<br>Telemetry Data Area 2|Event FIFO 1 exists in<br>Telemetry Data Area 2|
|TELDF-18|160|Event FIFO<br>1 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-19|161|Event FIFO<br>2 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-19|161|Event FIFO<br>2 Data Area|1||00h|Event FIFO 2 does not exist|Event FIFO 2 does not exist|
|TELDF-19|161|Event FIFO<br>2 Data Area|1||01h|Event FIFO 2 exists in<br>Telemetry Data Area 1|Event FIFO 2 exists in<br>Telemetry Data Area 1|
|TELDF-19|161|Event FIFO<br>2 Data Area|1||02h|Event FIFO 2 exists in<br>Telemetry Data Area 2|Event FIFO 2 exists in<br>Telemetry Data Area 2|
|TELDF-19|161|Event FIFO<br>2 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-20|162|Event FIFO<br>3 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-20|162|Event FIFO<br>3 Data Area|1||00h|Event FIFO 3 does not exist|Event FIFO 3 does not exist|
|TELDF-20|162|Event FIFO<br>3 Data Area|1||01h|Event FIFO 3 exists in<br>Telemetry Data Area 1|Event FIFO 3 exists in<br>Telemetry Data Area 1|
|TELDF-20|162|Event FIFO<br>3 Data Area|1||02h|Event FIFO 3 exists in<br>Telemetry Data Area 2|Event FIFO 3 exists in<br>Telemetry Data Area 2|
|TELDF-20|162|Event FIFO<br>3 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-21|163|Event FIFO<br>4 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-21|163|Event FIFO<br>4 Data Area|1||00h|Event FIFO 4 does not exist|Event FIFO 4 does not exist|
|TELDF-21|163|Event FIFO<br>4 Data Area|1||01h|Event FIFO 4 exists in<br>Telemetry Data Area 1|Event FIFO 4 exists in<br>Telemetry Data Area 1|
|TELDF-21|163|Event FIFO<br>4 Data Area|1||02h|Event FIFO 4 exists in<br>Telemetry Data Area 2|Event FIFO 4 exists in<br>Telemetry Data Area 2|
|TELDF-21|163|Event FIFO<br>4 Data Area|1||03h - FFh|Reserved|Reserved|

<!-- page 116 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|TELDF-22|164|Event FIFO<br>5 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-22|164|Event FIFO<br>5 Data Area|1||00h|Event FIFO 5 does not exist|Event FIFO 5 does not exist|
|TELDF-22|164|Event FIFO<br>5 Data Area|1||01h|Event FIFO 5 exists in<br>Telemetry Data Area 1|Event FIFO 5 exists in<br>Telemetry Data Area 1|
|TELDF-22|164|Event FIFO<br>5 Data Area|1||02h|Event FIFO 5 exists in<br>Telemetry Data Area 2|Event FIFO 5 exists in<br>Telemetry Data Area 2|
|TELDF-22|164|Event FIFO<br>5 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-23|165|Event FIFO<br>6 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-23|165|Event FIFO<br>6 Data Area|1||00h|Event FIFO 6 does not exist|Event FIFO 6 does not exist|
|TELDF-23|165|Event FIFO<br>6 Data Area|1||01h|Event FIFO 6 exists in<br>Telemetry Data Area 1|Event FIFO 6 exists in<br>Telemetry Data Area 1|
|TELDF-23|165|Event FIFO<br>6 Data Area|1||02h|Event FIFO 6 exists in<br>Telemetry Data Area 2|Event FIFO 6 exists in<br>Telemetry Data Area 2|
|TELDF-23|165|Event FIFO<br>6 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-24|166|Event FIFO<br>7 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-24|166|Event FIFO<br>7 Data Area|1||00h|Event FIFO 7 does not exist|Event FIFO 7 does not exist|
|TELDF-24|166|Event FIFO<br>7 Data Area|1||01h|Event FIFO 7 exists in<br>Telemetry Data Area 1|Event FIFO 7 exists in<br>Telemetry Data Area 1|
|TELDF-24|166|Event FIFO<br>7 Data Area|1||02h|Event FIFO 7 exists in<br>Telemetry Data Area 2|Event FIFO 7 exists in<br>Telemetry Data Area 2|
|TELDF-24|166|Event FIFO<br>7 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-25|167|Event FIFO<br>8 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-25|167|Event FIFO<br>8 Data Area|1||00h|Event FIFO 8 does not exist|Event FIFO 8 does not exist|
|TELDF-25|167|Event FIFO<br>8 Data Area|1||01h|Event FIFO 8 exists in<br>Telemetry Data Area 1|Event FIFO 8 exists in<br>Telemetry Data Area 1|
|TELDF-25|167|Event FIFO<br>8 Data Area|1||02h|Event FIFO 8 exists in<br>Telemetry Data Area 2|Event FIFO 8 exists in<br>Telemetry Data Area 2|
|TELDF-25|167|Event FIFO<br>8 Data Area|1||03h - FFh|Reserved|Reserved|
|TELDF-26|168|Event FIFO<br>9 Data Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-26|168|Event FIFO<br>9 Data Area|1||00h|Event FIFO 9 does not exist|Event FIFO 9 does not exist|
|TELDF-26|168|Event FIFO<br>9 Data Area|1||01h|Event FIFO 9 exists in<br>Telemetry Data Area 1|Event FIFO 9 exists in<br>Telemetry Data Area 1|
|TELDF-26|168|Event FIFO<br>9 Data Area|1||02h|Event FIFO 9 exists in<br>Telemetry Data Area 2|Event FIFO 9 exists in<br>Telemetry Data Area 2|
|TELDF-26|168|Event FIFO<br>9 Data Area|1||03h - FFh|Reserved|Reserved|

<!-- page 117 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|TELDF-27|169|Event FIFO<br>10 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-27|169|Event FIFO<br>10 Data<br>Area|1||00h|Event FIFO 10 does not exist|Event FIFO 10 does not exist|
|TELDF-27|169|Event FIFO<br>10 Data<br>Area|1||01h|Event FIFO 10 exists in<br>Telemetry Data Area 1|Event FIFO 10 exists in<br>Telemetry Data Area 1|
|TELDF-27|169|Event FIFO<br>10 Data<br>Area|1||02h|Event FIFO 10 exists in<br>Telemetry Data Area 2|Event FIFO 10 exists in<br>Telemetry Data Area 2|
|TELDF-27|169|Event FIFO<br>10 Data<br>Area|1||03h - FFh|Reserved|Reserved|
|TELDF-28|170|Event FIFO<br>11 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-28|170|Event FIFO<br>11 Data<br>Area|1||00h|Event FIFO 11 does not exist|Event FIFO 11 does not exist|
|TELDF-28|170|Event FIFO<br>11 Data<br>Area|1||01h|Event FIFO 11 exists in<br>Telemetry Data Area 1|Event FIFO 11 exists in<br>Telemetry Data Area 1|
|TELDF-28|170|Event FIFO<br>11 Data<br>Area|1||02h|Event FIFO 11 exists in<br>Telemetry Data Area 2|Event FIFO 11 exists in<br>Telemetry Data Area 2|
|TELDF-28|170|Event FIFO<br>11 Data<br>Area|1||03h - FFh|Reserved|Reserved|
|TELDF-29|171|Event FIFO<br>12 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-29|171|Event FIFO<br>12 Data<br>Area|1||00h|Event FIFO 12 does not exist|Event FIFO 12 does not exist|
|TELDF-29|171|Event FIFO<br>12 Data<br>Area|1||01h|Event FIFO 12 exists in<br>Telemetry Data Area 1|Event FIFO 12 exists in<br>Telemetry Data Area 1|
|TELDF-29|171|Event FIFO<br>12 Data<br>Area|1||02h|Event FIFO 12 exists in<br>Telemetry Data Area 2|Event FIFO 12 exists in<br>Telemetry Data Area 2|
|TELDF-29|171|Event FIFO<br>12 Data<br>Area|1||03h - FFh|Reserved|Reserved|
|TELDF-30|172|Event FIFO<br>13 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-30|172|Event FIFO<br>13 Data<br>Area|1||00h|Event FIFO 13 does not exist|Event FIFO 13 does not exist|
|TELDF-30|172|Event FIFO<br>13 Data<br>Area|1||01h|Event FIFO 13 exists in<br>Telemetry Data Area 1|Event FIFO 13 exists in<br>Telemetry Data Area 1|
|TELDF-30|172|Event FIFO<br>13 Data<br>Area|1||02h|Event FIFO 13 exists in<br>Telemetry Data Area 2|Event FIFO 13 exists in<br>Telemetry Data Area 2|
|TELDF-30|172|Event FIFO<br>13 Data<br>Area|1||03h - FFh|Reserved|Reserved|
|TELDF-31|173|Event FIFO<br>14 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-31|173|Event FIFO<br>14 Data<br>Area|1||00h|Event FIFO 14 does not exist|Event FIFO 14 does not exist|
|TELDF-31|173|Event FIFO<br>14 Data<br>Area|1||01h|Event FIFO 14 exists in<br>Telemetry Data Area 1|Event FIFO 14 exists in<br>Telemetry Data Area 1|
|TELDF-31|173|Event FIFO<br>14 Data<br>Area|1||02h|Event FIFO 14 exists in<br>Telemetry Data Area 2|Event FIFO 14 exists in<br>Telemetry Data Area 2|
|TELDF-31|173|Event FIFO<br>14 Data<br>Area|1||03h - FFh|Reserved|Reserved|

<!-- page 118 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|TELDF-32|174|Event FIFO<br>15 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-32|174|Event FIFO<br>15 Data<br>Area|1||00h|Event FIFO 15 does not exist|Event FIFO 15 does not exist|
|TELDF-32|174|Event FIFO<br>15 Data<br>Area|1||01h|Event FIFO 15 exists in<br>Telemetry Data Area 1|Event FIFO 15 exists in<br>Telemetry Data Area 1|
|TELDF-32|174|Event FIFO<br>15 Data<br>Area|1||02h|Event FIFO 15 exists in<br>Telemetry Data Area 2|Event FIFO 15 exists in<br>Telemetry Data Area 2|
|TELDF-32|174|Event FIFO<br>15 Data<br>Area|1||03h - FFh|Reserved|Reserved|
|TELDF-33|175|Event FIFO<br>16 Data<br>Area|1||**Event FIFO**<br>**Data Area**|**Description**||
|TELDF-33|175|Event FIFO<br>16 Data<br>Area|1||00h|Event FIFO 16 does not exist|Event FIFO 16 does not exist|
|TELDF-33|175|Event FIFO<br>16 Data<br>Area|1||01h|Event FIFO 16 exists in<br>Telemetry Data Area 1|Event FIFO 16 exists in<br>Telemetry Data Area 1|
|TELDF-33|175|Event FIFO<br>16 Data<br>Area|1||02h|Event FIFO 16 exists in<br>Telemetry Data Area 2|Event FIFO 16 exists in<br>Telemetry Data Area 2|
|TELDF-33|175|Event FIFO<br>16 Data<br>Area|1||03h - FFh|Reserved|Reserved|
|TELDF-34|183:176|Event FIFO<br>1 Start|8|Shall be set to the Dword offset of Event FIFO 1<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 1<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 1<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 1<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-35|191:184|Event FIFO<br>1 Size|8|This field shall contain the size of Event FIFO 1 in<br>Dwords.|This field shall contain the size of Event FIFO 1 in<br>Dwords.|This field shall contain the size of Event FIFO 1 in<br>Dwords.|This field shall contain the size of Event FIFO 1 in<br>Dwords.|
|TELDF-36|199:192|Event FIFO<br>2 Start|8|Shall be set to the Dword offset of Event FIFO 2<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 2<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 2<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 2<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-37|207:200|Event FIFO<br>2 Size|8|This field shall contain the size of Event FIFO 2 in<br>Dwords.|This field shall contain the size of Event FIFO 2 in<br>Dwords.|This field shall contain the size of Event FIFO 2 in<br>Dwords.|This field shall contain the size of Event FIFO 2 in<br>Dwords.|
|TELDF-38|215:208|Event FIFO<br>3 Start|8|Shall be set to the Dword offset of Event FIFO 3<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 3<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 3<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 3<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-39|223:216|Event FIFO<br>3 Size|8|This field shall contain the size of Event FIFO 3 in<br>Dwords.|This field shall contain the size of Event FIFO 3 in<br>Dwords.|This field shall contain the size of Event FIFO 3 in<br>Dwords.|This field shall contain the size of Event FIFO 3 in<br>Dwords.|
|TELDF-40|231:224|Event FIFO<br>4 Start|8|Shall be set to the Dword offset of Event FIFO 4<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 4<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 4<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 4<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-41|239:232|Event FIFO<br>4 Size|8|This field shall contain the size of Event FIFO 4 in<br>Dwords.|This field shall contain the size of Event FIFO 4 in<br>Dwords.|This field shall contain the size of Event FIFO 4 in<br>Dwords.|This field shall contain the size of Event FIFO 4 in<br>Dwords.|
|TELDF-42|247:240|Event FIFO<br>5 Start|8|Shall be set to the Dword offset of Event FIFO 5<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 5<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 5<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 5<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-43|255:248|Event FIFO<br>5 Size|8|This field shall contain the size of Event FIFO 5 in<br>Dwords|This field shall contain the size of Event FIFO 5 in<br>Dwords|This field shall contain the size of Event FIFO 5 in<br>Dwords|This field shall contain the size of Event FIFO 5 in<br>Dwords|
|TELDF-44|263:256|Event FIFO<br>6 Start|8|Shall be set to the Dword offset of Event FIFO 6<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 6<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 6<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|Shall be set to the Dword offset of Event FIFO 6<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|

<!-- page 119 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELDF-45|271:264|Event FIFO<br>6 Size|8|This field shall contain the size of Event FIFO 6 in<br>Dwords.|
|TELDF-46|279:272|Event FIFO<br>7 Start|8|Shall be set to the Dword offset of Event FIFO 7<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-47|287:280|Event FIFO<br>7 Size|8|This field shall contain the size of Event FIFO 7 in<br>Dwords.|
|TELDF-48|295:288|Event FIFO<br>8 Start|8|Shall be set to the Dword offset of Event FIFO 8<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-49|303:296|Event FIFO<br>8 Size|8|This field shall contain the size of Event FIFO 8 in<br>Dwords.|
|TELDF-50|311:304|Event FIFO<br>9 Start|8|Shall be set to the Dword offset of Event FIFO 9<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-51|319:312|Event FIFO<br>9 Size|8|This field shall contain the size of Event FIFO 9 in<br>Dwords.|
|TELDF-52|327:320|Event FIFO<br>10 Start|8|Shall be set to the Dword offset of Event FIFO 10<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-53|335:328|Event FIFO<br>10 Size|8|This field shall contain the size of Event FIFO 10 in<br>Dwords.|
|TELDF-54|343:336|Event FIFO<br>11 Start|8|Shall be set to the Dword offset of Event FIFO 11<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-55|351:344|Event FIFO<br>11 Size|8|This field shall contain the size of Event FIFO 11 in<br>Dwords.|
|TELDF-56|359:352|Event FIFO<br>12 Start|8|Shall be set to the Dword offset of Event FIFO 12<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-57|367:360|Event FIFO<br>12 Size|8|This field shall contain the size of Event FIFO 12 in<br>Dwords.|
|TELDF-58|375:368|Event FIFO<br>13 Start|8|Shall be set to the Dword offset of Event FIFO 13<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-59|383:376|Event FIFO<br>13 Size|8|This field shall contain the size of Event FIFO 13 in<br>Dwords.|
|TELDF-60|391:384|Event FIFO<br>14 Start|8|Shall be set to the Dword offset of Event FIFO 14<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-61|399:392|Event FIFO<br>14 Size|8|This field shall contain the size of Event FIFO 14 in<br>Dwords.|

<!-- page 120 -->
|Requirement<br>ID|Byte<br>Address|Field|# of Bytes|Field Description|
|---|---|---|---|---|
|TELDF-62|407:400|Event FIFO<br>15 Start|8|Shall be set to the Dword offset of Event FIFO 15<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-63|415:408|Event FIFO<br>15 Size|8|This field shall contain the size of Event FIFO 15 in<br>Dwords.|
|TELDF-64|423:416|Event FIFO<br>16 Start|8|Shall be set to the Dword offset of Event FIFO 16<br>starting from Dword 0 / byte 0 of the selected<br>Telemetry Data Area.|
|TELDF-65|431:424|Event FIFO<br>16 Size|8|This field shall contain the size of Event FIFO 16 in<br>Dwords.|
|TELDF-66|511:432|Reserved|80|Shall be cleared to zero.|
|TELDF-67|1023:512|SMART /<br>Health<br>Information|512|This shall be a copy of the SMART / Health<br>Information log page (Log Identifier 02h) of the<br>controller that captured the Telemetry data.|
|TELDF-68|1535:1024|SMART /<br>Health<br>Information<br>Extended|512|This shall be a copy of the SMART / Health<br>Information Extended (Log Identifier C0h) data of<br>the controller that captured the Telemetry data.|

The order and placement of the Event and Statistics FIFOs are vendor unique and shall be placed in the
Telemetry log page Data Area 1 after byte offset 1535 up to the end of Data Area 1.

### **4.10 Device Self-test Requirements**

To normalize the reporting of Device Self-test data, the following Segment Numbers are defined.

|Requirement ID|Description|
|---|---|
|SELFTST-1|The device shall use the following segment numbers:<br>**Segment**<br>**Test Performed**<br>**Failure Criteria**<br>0 <br>Reserved.<br>N/A<br>1 – SRAM<br>Check<br>Write a test pattern to SRAM<br>followed by a read and compare of<br>original data. Shall test all internal<br>and external SRAM devices.<br>Any uncorrectable error or<br>data miscompare.<br>2 – SMART<br>Check<br>Check SMART or health status for<br>Critical Warning bits set to 1b in<br>SMART / Health Information log<br>page.<br>Any Critical Warning bit set to<br>1b fails this segment, with the<br>exception of bit 0 (spare<br>capacity below threshold) and<br>bit 1 (thermal excursions).|

|Segment|Test Performed|Failure Criteria|
|---|---|---|
|0|Reserved.|N/A|
|1 – SRAM<br>Check|Write a test pattern to SRAM<br>followed by a read and compare of<br>original data. Shall test all internal<br>and external SRAM devices.|Any uncorrectable error or<br>data miscompare.|
|2 – SMART<br>Check|Check SMART or health status for<br>Critical Warning bits set to 1b in<br>SMART / Health Information log<br>page.|Any Critical Warning bit set to<br>1b fails this segment, with the<br>exception of bit 0 (spare<br>capacity below threshold) and<br>bit 1 (thermal excursions).|

<!-- page 121 -->
|Requirement ID|Description|Col3|Col4|Col5|Col6|
|---|---|---|---|---|---|
|||3 – Volatile<br>Memory<br>Backup|Validate volatile memory backup<br>solution health.<br>Measure backup power source<br>charge and/or discharge time.<br>Shall perform backup test and not<br>rely on previous results.<br>During the test, the device shall not<br>lose power loss protection.|Significant degradation in<br>backup capability.||
|||4 – Non-User<br>Data<br>Validation|Confirm/validate all copies of non-<br>user data (e.g., FTL, log pages, etc.).|Non-user data is corrupt and<br>is not recoverable.|Non-user data is corrupt and<br>is not recoverable.|
|||5 – NVM<br>Integrity|Write/read/compare to reserved<br>areas of each NVM, if present.<br>Ensure that every read/write channel<br>of the controller is exercised and<br>each NVM is accessed.|Data miscompare or hardware<br>failure.|Data miscompare or hardware<br>failure.|
|||6 – Data<br>Integrity|Perform background housekeeping<br>tasks, prioritizing actions that<br>enhance the integrity of stored data.<br>Test CRC hardware, error correction<br>hardware, including XOR, encryption<br>engine, etc.|Any failure of the CRC<br>hardware, error correction<br>hardware, including XOR,<br>encryption engine, etc. or any<br>uncorrectable data error not<br>caused by Write<br>Uncorrectable command(s).|Any failure of the CRC<br>hardware, error correction<br>hardware, including XOR,<br>encryption engine, etc. or any<br>uncorrectable data error not<br>caused by Write<br>Uncorrectable command(s).|
|||7 – Media<br>Check<br>Extended|Perform reads from every mapped<br>LBA.<br>Shall include LBA 0 and MAXLBA, if<br>mapped.<br>Shall terminate segment when all<br>mapped LBAs are read, or the Device<br>Self-test completion time limit<br>expires.|Any uncorrectable error not<br>caused by Write<br>Uncorrectable command(s).|Any uncorrectable error not<br>caused by Write<br>Uncorrectable command(s).|
|||8 – DRAM<br>check|Write a test pattern to DRAM<br>followed by a read and compare of<br>original data.  Shall test all internal<br>and external SRAM devices.|Any uncorrectable error or<br>data miscompare.|Any uncorrectable error or<br>data miscompare.|
|||9 –<br>Temperature<br>Sensor|Verify the temperature sensors are<br>working correctly.|Temperature sensors are not<br>reporting correctly.|Temperature sensors are not<br>reporting correctly.|
|||10 – SMART<br>Check|Same as 2-SMART Check.  This check<br>shall be performed after all other test<br>segments in order to detect critical<br>warnings caused by prior test<br>segments.|Any Critical Warning bit set to<br>1b fails this segment, with the<br>exception of bit 0 (spare<br>capacity below threshold) and<br>bit 1 (thermal excursions).|Any Critical Warning bit set to<br>1b fails this segment, with the<br>exception of bit 0 (spare<br>capacity below threshold) and<br>bit 1 (thermal excursions).|
|||200:11|Reserved.|N/A|N/A|

<!-- page 122 -->
|Requirement ID|Description|Col3|Col4|Col5|Col6|
|---|---|---|---|---|---|
|||255:201|Vendor Unique. Any Vendor Unique<br>Segment Numbers shall be clearly<br>documented and disclosed to the<br>customer.|||
|SELFTST-2|A short device self-test operation (i.e., the STC field is set to 1h) shall complete in less than<br>or equal to 2 minutes.|A short device self-test operation (i.e., the STC field is set to 1h) shall complete in less than<br>or equal to 2 minutes.|A short device self-test operation (i.e., the STC field is set to 1h) shall complete in less than<br>or equal to 2 minutes.|A short device self-test operation (i.e., the STC field is set to 1h) shall complete in less than<br>or equal to 2 minutes.|A short device self-test operation (i.e., the STC field is set to 1h) shall complete in less than<br>or equal to 2 minutes.|
|SELFTST-3|An extended device self-test operation (i.e., the STC field is set to 2h) shall complete in less<br>than or equal to 30 minutes (i.e., the EDSTT field shall indicate a value of less than or equal<br>to 30 minutes).|An extended device self-test operation (i.e., the STC field is set to 2h) shall complete in less<br>than or equal to 30 minutes (i.e., the EDSTT field shall indicate a value of less than or equal<br>to 30 minutes).|An extended device self-test operation (i.e., the STC field is set to 2h) shall complete in less<br>than or equal to 30 minutes (i.e., the EDSTT field shall indicate a value of less than or equal<br>to 30 minutes).|An extended device self-test operation (i.e., the STC field is set to 2h) shall complete in less<br>than or equal to 30 minutes (i.e., the EDSTT field shall indicate a value of less than or equal<br>to 30 minutes).|An extended device self-test operation (i.e., the STC field is set to 2h) shall complete in less<br>than or equal to 30 minutes (i.e., the EDSTT field shall indicate a value of less than or equal<br>to 30 minutes).|
|SELFTST-4|A vendor-specific self-test operation (i.e., the STC field is set to Eh) shall complete the test<br>specified by SELFTST-7 in less than or equal to 2 seconds.|A vendor-specific self-test operation (i.e., the STC field is set to Eh) shall complete the test<br>specified by SELFTST-7 in less than or equal to 2 seconds.|A vendor-specific self-test operation (i.e., the STC field is set to Eh) shall complete the test<br>specified by SELFTST-7 in less than or equal to 2 seconds.|A vendor-specific self-test operation (i.e., the STC field is set to Eh) shall complete the test<br>specified by SELFTST-7 in less than or equal to 2 seconds.|A vendor-specific self-test operation (i.e., the STC field is set to Eh) shall complete the test<br>specified by SELFTST-7 in less than or equal to 2 seconds.|
|SELFTST-5|A device self-test operation shall not fail if it is unable to complete within the specified<br>completion time (e.g., due to concurrent host I/O activity). The device shall complete as<br>many device self-test segments as possible within the allotted completion time.|A device self-test operation shall not fail if it is unable to complete within the specified<br>completion time (e.g., due to concurrent host I/O activity). The device shall complete as<br>many device self-test segments as possible within the allotted completion time.|A device self-test operation shall not fail if it is unable to complete within the specified<br>completion time (e.g., due to concurrent host I/O activity). The device shall complete as<br>many device self-test segments as possible within the allotted completion time.|A device self-test operation shall not fail if it is unable to complete within the specified<br>completion time (e.g., due to concurrent host I/O activity). The device shall complete as<br>many device self-test segments as possible within the allotted completion time.|A device self-test operation shall not fail if it is unable to complete within the specified<br>completion time (e.g., due to concurrent host I/O activity). The device shall complete as<br>many device self-test segments as possible within the allotted completion time.|
|SELFTST-6|For a Self-test Code (STC) of 2h, the device self-test operation shall terminate upon reading<br>all allocated LBAs and completing all non-media related tests.|For a Self-test Code (STC) of 2h, the device self-test operation shall terminate upon reading<br>all allocated LBAs and completing all non-media related tests.|For a Self-test Code (STC) of 2h, the device self-test operation shall terminate upon reading<br>all allocated LBAs and completing all non-media related tests.|For a Self-test Code (STC) of 2h, the device self-test operation shall terminate upon reading<br>all allocated LBAs and completing all non-media related tests.|For a Self-test Code (STC) of 2h, the device self-test operation shall terminate upon reading<br>all allocated LBAs and completing all non-media related tests.|
|SELFTST-7|For a Device Self-test Code (STC) of 1h or Eh, the device self-test operation shall include at<br>a minimum, segments 1 to 3 and 8, and as much as possible of segments 4 to 7, within the<br>completion time specified for that specific operation.|For a Device Self-test Code (STC) of 1h or Eh, the device self-test operation shall include at<br>a minimum, segments 1 to 3 and 8, and as much as possible of segments 4 to 7, within the<br>completion time specified for that specific operation.|For a Device Self-test Code (STC) of 1h or Eh, the device self-test operation shall include at<br>a minimum, segments 1 to 3 and 8, and as much as possible of segments 4 to 7, within the<br>completion time specified for that specific operation.|For a Device Self-test Code (STC) of 1h or Eh, the device self-test operation shall include at<br>a minimum, segments 1 to 3 and 8, and as much as possible of segments 4 to 7, within the<br>completion time specified for that specific operation.|For a Device Self-test Code (STC) of 1h or Eh, the device self-test operation shall include at<br>a minimum, segments 1 to 3 and 8, and as much as possible of segments 4 to 7, within the<br>completion time specified for that specific operation.|
|SELFTST-8|Obsolete. See SELFTST-1 segments 2 and 10.|Obsolete. See SELFTST-1 segments 2 and 10.|Obsolete. See SELFTST-1 segments 2 and 10.|Obsolete. See SELFTST-1 segments 2 and 10.|Obsolete. See SELFTST-1 segments 2 and 10.|
|SELFTST-9|The device vendor shall provide the minimum number of LBAs required to be written by<br>the host to enable the extended device self-test operation to read from all physical non-<br>volatile memory elements (e.g., NAND die). A segment shall not fail solely due to the host<br>writing less than the minimum number of LBAs.|The device vendor shall provide the minimum number of LBAs required to be written by<br>the host to enable the extended device self-test operation to read from all physical non-<br>volatile memory elements (e.g., NAND die). A segment shall not fail solely due to the host<br>writing less than the minimum number of LBAs.|The device vendor shall provide the minimum number of LBAs required to be written by<br>the host to enable the extended device self-test operation to read from all physical non-<br>volatile memory elements (e.g., NAND die). A segment shall not fail solely due to the host<br>writing less than the minimum number of LBAs.|The device vendor shall provide the minimum number of LBAs required to be written by<br>the host to enable the extended device self-test operation to read from all physical non-<br>volatile memory elements (e.g., NAND die). A segment shall not fail solely due to the host<br>writing less than the minimum number of LBAs.|The device vendor shall provide the minimum number of LBAs required to be written by<br>the host to enable the extended device self-test operation to read from all physical non-<br>volatile memory elements (e.g., NAND die). A segment shall not fail solely due to the host<br>writing less than the minimum number of LBAs.|
|SELFTST-10|If the Device Self-test command is reissued after a previous Device Self-test command and<br>operation completed successfully, then the Media Check Extended (segment 7) shall test<br>different LBAs, wrapping around if necessary. For example, if the device contains 10000h<br>allocated LBAs, but only 6000h LBAs are able to be scanned within the specified Device<br>Self-test completion time, then the first run of the Device Self-test would scan LBAs 0h to<br>5FFFh, the next run would scan LBAs 6000h to BFFFh and the next would scan LBAs<br>beginning at C000h wrapping to 0h and then to 1FFFh, and so forth.|If the Device Self-test command is reissued after a previous Device Self-test command and<br>operation completed successfully, then the Media Check Extended (segment 7) shall test<br>different LBAs, wrapping around if necessary. For example, if the device contains 10000h<br>allocated LBAs, but only 6000h LBAs are able to be scanned within the specified Device<br>Self-test completion time, then the first run of the Device Self-test would scan LBAs 0h to<br>5FFFh, the next run would scan LBAs 6000h to BFFFh and the next would scan LBAs<br>beginning at C000h wrapping to 0h and then to 1FFFh, and so forth.|If the Device Self-test command is reissued after a previous Device Self-test command and<br>operation completed successfully, then the Media Check Extended (segment 7) shall test<br>different LBAs, wrapping around if necessary. For example, if the device contains 10000h<br>allocated LBAs, but only 6000h LBAs are able to be scanned within the specified Device<br>Self-test completion time, then the first run of the Device Self-test would scan LBAs 0h to<br>5FFFh, the next run would scan LBAs 6000h to BFFFh and the next would scan LBAs<br>beginning at C000h wrapping to 0h and then to 1FFFh, and so forth.|If the Device Self-test command is reissued after a previous Device Self-test command and<br>operation completed successfully, then the Media Check Extended (segment 7) shall test<br>different LBAs, wrapping around if necessary. For example, if the device contains 10000h<br>allocated LBAs, but only 6000h LBAs are able to be scanned within the specified Device<br>Self-test completion time, then the first run of the Device Self-test would scan LBAs 0h to<br>5FFFh, the next run would scan LBAs 6000h to BFFFh and the next would scan LBAs<br>beginning at C000h wrapping to 0h and then to 1FFFh, and so forth.|If the Device Self-test command is reissued after a previous Device Self-test command and<br>operation completed successfully, then the Media Check Extended (segment 7) shall test<br>different LBAs, wrapping around if necessary. For example, if the device contains 10000h<br>allocated LBAs, but only 6000h LBAs are able to be scanned within the specified Device<br>Self-test completion time, then the first run of the Device Self-test would scan LBAs 0h to<br>5FFFh, the next run would scan LBAs 6000h to BFFFh and the next would scan LBAs<br>beginning at C000h wrapping to 0h and then to 1FFFh, and so forth.|
|SELFTST-11|The device self-test operation shall not be destructive to any user data (note that reading<br>user data once during the device self-test operation is not considered destructive, because<br>even though it technically causes read disturb, the effect is minimal).|The device self-test operation shall not be destructive to any user data (note that reading<br>user data once during the device self-test operation is not considered destructive, because<br>even though it technically causes read disturb, the effect is minimal).|The device self-test operation shall not be destructive to any user data (note that reading<br>user data once during the device self-test operation is not considered destructive, because<br>even though it technically causes read disturb, the effect is minimal).|The device self-test operation shall not be destructive to any user data (note that reading<br>user data once during the device self-test operation is not considered destructive, because<br>even though it technically causes read disturb, the effect is minimal).|The device self-test operation shall not be destructive to any user data (note that reading<br>user data once during the device self-test operation is not considered destructive, because<br>even though it technically causes read disturb, the effect is minimal).|

### **4.11 Firmware Update Requirements**

This defines the requirements for firmware update in the device.

|Requirement ID|Description|
|---|---|
|FWUP-1|Obsolete. SeeSTD-LOG-10.|
|<br>FWUP-2|<br>Other than media end-of-life, devices shall not have any restrictions on the number of<br>firmware downloads supported.|

<!-- page 123 -->
|Requirement ID|Description|
|---|---|
|FWUP-3|The Firmware Commit command with the following Commit Action (CA) codes shall be<br>supported:<br>• <br>000b – Download only.<br>• <br>001b – Download and activate upon reset.<br>• <br>010b – Activate upon reset.<br>• <br>011b – Activate immediately without reset.|
|FWUP-4|Firmware Image Download command shall be supported and shall not cause any<br>performance impact.|
|FWUP-5|Obsolete.|
|FWUP-6|The device shall support a minimum of 2 read/write slots for firmware update and may<br>support up to 7.|
|FWUP-7|For firmware commit action 011b (firmware activation without reset), the device shall<br>complete the firmware activation process and be ready to accept host I/O and NVMe<br>Admin commands within 1 second from the receipt of the Firmware Commit command.<br>The Maximum Time for Firmware Activation (MTFA) field shall not exceed Ah.|
|FWUP-8|If a Firmware Commit command is processed that specifies a Security Firmware Revision<br>(seeSMART-22) that is less than the Security Firmware of the actively running firmware<br>revision, then the device shall return a status code of Firmware Activation Prohibited<br>(13h).<br>If a firmware image is committed/activated that has a Security Firmware Revision that is<br>greater than or equal to the Security Firmware Revision of the actively running firmware<br>revision, then the operation shall be permitted.|
|FWUP-9|The firmware image in each valid firmware slot shall have multiple copies of that firmware<br>image on separate physical non-volatile memory devices (e.g., NAND die, NAND RAID<br>stripe) for reliability.|
|FWUP-10|Firmware activation shall not cause or require data (e.g., user data, log page contents, etc.)<br>to be lost or destroyed.|
|FWUP-11|Firmware activation without reset shall occur seamlessly on a running system:<br>• <br>The device shall preserve the current state of the device (e.g., Opal locking state,<br>current value of each Feature, Timestamp, I/O Submission/Completion Queue setup,<br>NVMe-MI state such as MCTP Transmission Unit Size, SMBus/I2C Frequency, and<br>MCTP state such as the MCTP endpoint ID, LBA format, PCIe state, etc.).<br>• <br>The PCIe link state shall not be impacted.|
|FWUP-12|The firmware image shall contain the firmware for all the device’s controllers (NVMe<br>controllers, management controllers, etc.).|
|FWUP-13|The VPD/FRU Data shall be a part of the device’s firmware update image and shall be field<br>upgradable using the standard NVMe Firmware Image Download/Firmware Commit<br>commands.  VPD fields that are unique to the device (e.g., Serial Number) shall be<br>preserved during a firmware update.|
|FWUP-14|The size of the firmware shall be 6 MiB or less in order to facilitate firmware update via<br>low-bandwidth interfaces (e.g., NVMe-MI over SMBus/PCIe VDM).|

<!-- page 124 -->
|Requirement ID|Description|
|---|---|
|FWUP-15|Requiring a reset of any type to activate firmware under any condition shall be avoided. If<br>a reset is unavoidable, the device vendor shall request a waiver from the end customer. In<br>cases where waivers are granted, a Controller Level Reset is preferred over a Conventional<br>Reset. Firmware Activation requiring an NVMe Subsystem Reset should always be<br>avoided.|
|FWUP-16|All firmware updates shall be allowed to be performed by the system vendor or end user<br>without any outside assistance from NVMe device vendor employees or anyone else and<br>shall not require any additional vendor-specific actions or equipment (such as dongles,<br>debug cables, etc.) unless otherwise noted in this specification. This includes both pre-<br>production and production firmware.|
|FWUP-17|Firmware updates shall not require an intermediate firmware update or "bridge code" to<br>update from one firmware version to the next subsequent version (e.g., N-1 firmware<br>revision to bridge firmware to N firmware is prohibited). This includes both pre-<br>production and production firmware.|
|FWUP-18|The device shall not be left in an unusable state due to any reset or loss of power during a<br>firmware update. Depending on where in the device’s firmware activation process the<br>reset or loss of power occurs, the device shall either:<br>• <br>abort the firmware activation and continue running with the firmware revision that<br>was running at the start of the firmware update process; or<br>• <br>complete the firmware activation and start running with the new firmware revision.|
|FWUP-19|For production-level firmware, all means of updating the firmware besides the Firmware<br>Image Download/Firmware Commit commands (e.g., via MMIO or any vendor-proprietary<br>mechanisms) shall be disabled.|
|FWUP-20|The device shall support a read-only firmware slot (slot 1). If a firmware image is<br>successfully activated to a read-write slot that increases the Security Version Number (see<br>SMART-22), then the device shall also update the read-only slot 1 with that firmware<br>image.|
|FWUP-21|If the Firmware Slot field in the Firmware Commit command is cleared to 0h, then the<br>device shall commit the firmware image to a firmware slot that is not currently active.|
|FWUP-22|If the current active firmware image is corrupt, then the device shall automatically fail over<br>to another backup copy of that firmware image until all backup copies of that firmware<br>image are exhausted. The device shall not automatically fail over to another revision of<br>firmware in a different firmware slot, this overrides the NVM Express Base Specification.<br>The vendor should follow the guidelines in NIST SP 800-193.|
|FWUP-23|A single firmware image shall cover all the devices in a product family. For example,<br>devices with the same model but different capacity points, endurance or form factor shall<br>have one firmware image that works on all devices. A single firmware image shall cover all<br>TCG Opal capable and non-TCG Opal capable devices in a given product family.<br>An exception is that the firmware for a family of FIPS 140-3 compliant devices is different<br>than the firmware for the same family of non-FIPS 140-3 compliant devices. For example,<br>the firmware for the family of FIPS 140-3 compliant devices shall contain the FIPS security<br>descriptor whereas the firmware for the family of non-FIPS 140-3 compliant devices shall<br>not contain the FIPS security descriptor. Other than the FIPS security descriptor, the<br>firmware for the family of FIPS 140-3 compliant devices should be the same as the<br>firmware for the same family of non-FIPS 140-3 compliant devices.|

<!-- page 125 -->
|Requirement ID|Description|
|---|---|
|FWUP-24|Every firmware image shall have a firmware signature that meets the requirements of<br>SBT-1 and SBT-4. The device shall check the firmware signature as part of processing any<br>Firmware Commit command that commits a firmware image to a firmware slot. If the<br>firmware signature check fails, the device shall abort the Firmware Commit command with<br>Invalid Firmware Image status.|
|FWUP-25|When activating a firmware image to the same slot as the currently running firmware<br>(where the currently running firmware is the firmware that processed the Firmware<br>Commit command):<br>• <br>the device shall keep a copy of the currently running firmware until the newly<br>activated firmware completes initialization successfully at least once; and<br>• <br>if the newly activated firmware cannot complete initialization successfully, then the<br>device shall revert to the firmware that processed the Firmware Commit command;<br>and<br>• <br>once the newly activated firmware completes initialization successfully at least once,<br>the firmware image for the firmware that processed the Firmware Commit command<br>is permitted to be discarded.|
|FWUP-26|For firmware commit action 001b or 010b (firmware is activated at the next Controller<br>Level Reset), the device shall complete the firmware activation process within 5 seconds<br>from the start of the Controller Level Reset.|
|FWUP-27|For an active slot firmware update, upon completing the firmware activate of the new<br>firmware, the firmware slot shall only contain multiple copies of the active firmware with<br>no other additional information. When updating a firmware slot which is not active, upon<br>completing the Firmware Commit command, the firmware slot being updated shall only<br>contain multiple copies of the committed firmware with no other additional information.|
|FWUP-28|The Firmware Version value(s) in the FIPS 140-3 certification shall match the value(s)<br>indicated by the Firmware Revision field in the Identify Controller data structure.|
|FWUP-29|The device shall set the Firmware Update Granularity (FWUG) field to 01h indicating and<br>firmware update granularity of 4,096 bytes.|

### **4.12 Factory Default Requirements**

This section defines additional requirements for the state of the device as shipped from the supplier
factory. In addition to the factory default requirements in this section, factory default requirements listed
in other sections of this document are also required (e.g., NVMe-AD-22).

|Requirement ID|Description|
|---|---|
|FDEF-1|All firmware slots shall contain the most recent production firmware revision.|
|FDEF-2|All logical blocks shall be deallocated.|
|FDEF-3|The following SMART / Health Information log page fields shall be cleared to 0h: Critical<br>Warning, Endurance Group Critical Warning Summary, Data Units Read, Data Units<br>Written, Host Read Commands, Host Write Commands, Controller Busy Time, Power<br>Cycles, Power On Hours, Unsafe Shutdowns, Media, and Data Integrity Errors, Percentage<br>Used, and Number of Error Information Log Entries.|
|FDEF-4|The Available Spare field in the SMART / Health Information log page shall be set to a value<br>of 100.|

<!-- page 126 -->
|Requirement ID|Description|
|---|---|
|FDEF-5|The Total Number of Events field in the Persistent Event log page shall be cleared to 0h.|
|FDEF-6|All features that are saveable shall not have a saved value unless otherwise specified. This<br>requirement applies to features in the NVM Express Specifications and this specification.|

### **4.13 Deallocation Requirements**

|Requirement ID|Description|
|---|---|
|TRIM-1|The device shall support the Deallocate attribute of the Dataset Management command.|
|TRIM-2|Once the device has deallocated a logical block, a read of that logical block shall return all<br>bytes cleared to 0h until that logical block has been modified by a command (e.g., Write,<br>Copy, etc.) (i.e., bits 2:0 = 001b in the Deallocate Logical Block Features (DLFEAT) field in<br>the Identify Namespace data structure).|
|TRIM-3|Obsolete (see TRIM-2).|
|TRIM-4|Device deallocated logical blocks shall provide the performance and reliability benefits of<br>overprovisioned space.|
|TRIM-5|The device shall support Garbage Collection during periods of no I/O (Idle GC).|
|TRIM-6|Read latency shall not change more than 5% from baseline when the host is issuing<br>Deallocate/TRIM commands.|
|TRIM-7|Read latency shall not change more than 5% from baseline when the device is performing<br>Idle GC.|
|TRIM-8|If any device deallocated logical blocks have been subsequently read or written to, then<br>the contents of those logical blocks shall not change as a consequence of an unsafe power<br>down event.|
|TRIM-9|The device shall deallocate data to the maximum extent possible provided that it does not<br>violate TRIM-6 or TRIM-7.  Background deallocate processing is allowed provided that it<br>does not violate TRIM-8.|

### **4.14 Sector Size and Namespace Support**

|Requirement ID|Description|
|---|---|
|SECTOR-1|Obsolete.  Replaced by SECTOR-4.|
|SECTOR-2|Obsolete.  Replaced by SECTOR-4.|
|SECTOR-3|The device shall have one active Namespace whose size is the maximum capacity as<br>shipped from the factory.|
|SECTOR-4|The device shall support 512-byte and 4096-byte logical block sizes.|
|SECTOR-5|The capacity reported on the device label shall comply with the latest revision of the<br>SFF-8447 Specification for LBA Count for Disk Drives for all form factors, including form<br>factors not explicitly listed in the SFF-8447 Specification.|

### **4.15 Set/Get Features Requirements**

This section describes features defined by this specification. Unless otherwise specified, the device shall
support all the features defined in this section.

<!-- page 127 -->
**4.15.1 General Feature Requirements**

|Requirement ID|Description|
|---|---|
|GETF-1|For any Feature Identifier defined in this section, Selection (SEL) values 00b to 11b in<br>Dword 10 of the Get Features command shall be supported.|
|GETF-2|If the feature requested by Set Features or by Get Features is not supported, then a status<br>error code of 02h (Invalid Field in Command) shall be returned.|
|GETF-3|The device shall not implement a Feature with Feature Identifier D0h.|
|GETF-4|For any Feature Identifier defined in this section that is not Namespace scoped, the host<br>should either clear the Namespace Identifier (NSID) field in the Get Features command to<br>zero or set that field to FFFFFFFFh. In addition, the host may set that field to a valid NSID if<br>the feature is Namespace scoped. The device shall return the appropriate status based on<br>the NVM Express Specifications.|
|GETF-5|If the SEL field is set to 11b (i.e., Supported Features) in a Get Features command for any<br>Feature Identifier defined in this section, then the following capabilities for that Feature<br>Identifier shall be returned in CQE Dword 0:<br> <br>**Bit**<br>**Bit Name**<br>**Bit Value**<br>7:3<br>Reserved<br>0b<br>2 <br>Changeable (CHANG)<br>1b<br>1 <br>NS Specific (NSSPEC)<br>See below<br>0 <br>Saveable (SVBL)<br>See below<br> <br>If the scope of the Feature (seeSection 4.15.2 DSSD Feature Requirements) is Namespace,<br>then the NSSPEC bit shall be set to 1b, otherwise, the NSSPEC bit shall be cleared to 0b. if<br>the Feature is saveable (seeSection 4.15.2 DSSD Feature Requirements), then the SVBL bit<br>shall be set to 1b, otherwise the SVBL bit shall be cleared to 0b.|

127

|Bit|Bit Name|Bit Value|
|---|---|---|
|7:3|Reserved|0b|
|2|Changeable (CHANG)|1b|
|1|NS Specific (NSSPEC)|See below|
|0|Saveable (SVBL)|See below|

<!-- page 128 -->
**4.15.2 DSSD Feature Requirements**

The following table defines the scope and persistence for all DSSD specific Features:

|Feature Identifier|Scope|Persistence|Feature Name|Reference<br>Section|
|---|---|---|---|---|
|C0h|NVM subsystem|No|Error Injection|4.15.3|
|C1h|NVM subsystem|N/A|Obsolete|N/A|
|C2h|NVM subsystem|Saveable|EOL/PLP Failure Mode|4.15.5|
|C3h|Controller|No|Clear PCIe Correctable Error Counters|4.15.7|
|C4h|NVM subsystem|Saveable|Enable IEEE1667 Silo|4.15.9|
|C5h|Controller|Saveable|Latency Monitor|4.15.11|
|C6h|NVM subsystem|Saveable|PLP Health Check Interval|4.15.13|
|C7h|NVM subsystem|Saveable|DSSD Power State|4.15.15|
|C8h|NVM subsystem|Saveable|Telemetry Profile|4.15.17|
|C9h|Controller|No|DSSD Asynchronous Event Configuration|4.15.19|
|Scope KEY:<br>• <br>Namespace = The Set Feature affects a specific namespace.<br>• <br>Controller = The Set Feature affects the controller that is processing the command.<br>• <br>NVM subsystem = The Set Feature affects the NVM subsystem.<br>Persistence KEY:<br>• <br>Yes = Current setting persists across power cycles and resets and the Feature is not saveable.<br>• <br>No = Current setting does not persist across power cycles and resets and the Feature is not saveable.<br>• <br>Saveable = Current setting does not persist across power cycles and resets and the Feature is saveable.|Scope KEY:<br>• <br>Namespace = The Set Feature affects a specific namespace.<br>• <br>Controller = The Set Feature affects the controller that is processing the command.<br>• <br>NVM subsystem = The Set Feature affects the NVM subsystem.<br>Persistence KEY:<br>• <br>Yes = Current setting persists across power cycles and resets and the Feature is not saveable.<br>• <br>No = Current setting does not persist across power cycles and resets and the Feature is not saveable.<br>• <br>Saveable = Current setting does not persist across power cycles and resets and the Feature is saveable.|Scope KEY:<br>• <br>Namespace = The Set Feature affects a specific namespace.<br>• <br>Controller = The Set Feature affects the controller that is processing the command.<br>• <br>NVM subsystem = The Set Feature affects the NVM subsystem.<br>Persistence KEY:<br>• <br>Yes = Current setting persists across power cycles and resets and the Feature is not saveable.<br>• <br>No = Current setting does not persist across power cycles and resets and the Feature is not saveable.<br>• <br>Saveable = Current setting does not persist across power cycles and resets and the Feature is saveable.|Scope KEY:<br>• <br>Namespace = The Set Feature affects a specific namespace.<br>• <br>Controller = The Set Feature affects the controller that is processing the command.<br>• <br>NVM subsystem = The Set Feature affects the NVM subsystem.<br>Persistence KEY:<br>• <br>Yes = Current setting persists across power cycles and resets and the Feature is not saveable.<br>• <br>No = Current setting does not persist across power cycles and resets and the Feature is not saveable.<br>• <br>Saveable = Current setting does not persist across power cycles and resets and the Feature is saveable.|Scope KEY:<br>• <br>Namespace = The Set Feature affects a specific namespace.<br>• <br>Controller = The Set Feature affects the controller that is processing the command.<br>• <br>NVM subsystem = The Set Feature affects the NVM subsystem.<br>Persistence KEY:<br>• <br>Yes = Current setting persists across power cycles and resets and the Feature is not saveable.<br>• <br>No = Current setting does not persist across power cycles and resets and the Feature is not saveable.<br>• <br>Saveable = Current setting does not persist across power cycles and resets and the Feature is saveable.|

The device shall support the following additional vendor unique Set/Get Features Identifiers.

**4.15.3 Error Injection (Feature Identifier C0h) Set Features**

Feature to inject one or more error conditions to be reported by the device. If multiple Set Features
commands for this feature are sent by the host, then only information from the most recent successful
command is retained (i.e., subsequent commands replace information provided by previous commands).

|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SERRI-1|0|Command<br>Identifier (CID)|31:16|Should be set as defined in the NVM Express Base<br>Specification.|
|SERRI-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Should be cleared to 00b to specify that PRPs are used.|
|SERRI-3|0|Reserved|13:10|Should be cleared to zero.|
|SERRI-4|0|Fused Operation<br>(FUSE)|9:8|Should be cleared to 00b.|
|SERRI-5|0|Opcode (OPC)|7:0|Should be set to 09h.|
|SERRI-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|SERRI-7|3:2|Reserved|All|Should be cleared to zero.|

<!-- page 129 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SERRI-8|5:4|Metadata<br>Pointer (MPTR)|All|Should be cleared to zero.|
|SERRI-9|9:6|Data Pointer<br>(DPTR)|All|Should contain one or two PRPs that specify a physically<br>contiguous 4096-byte address range containing 0 to 127<br>Error Injection Data Structure Entries.|
|SERRI-10|10|Save (SV)|31|The device shall not support setting this bit to 1b.  If the<br>controller receives this Set Features command with the<br>bit set to 1b, then the device shall abort the command<br>with a status of Feature Identifier Not Saveable.|
|SERRI-11|10|Reserved|30:8|Should be cleared to zero.|
|SERRI-12|10|Feature<br>Identifier (FID)|7:0|Should be set to C0h.|
|SERRI-13|11|Reserved|31:7|Should be cleared to zero.|
|SERRI-14|11|Number of Error<br>Injections|6:0|This field should specify the number of valid Error<br>Injection Data Entries described in the address range<br>pointed to by the Data Pointer (DPTR) field.|
|SERRI-15|13:12|Reserved|All|Should be cleared to zero.|
|SERRI-16|14|UUID Index|31:0|Should be set perUUID-3.|
|SERRI-17|15|Reserved|31:0|Should be cleared to zero.|

|Requirement ID|Description|
|---|---|
|ERRI-1|The maximum number of entries in the Number of Error Injections field shall be 127.|
|ERRI-2|A value of 0000000b in the Number of Error Injections field shall clear any outstanding<br>error injection events.|
|ERRI-3|The error injections shall not overlap and may be listed in any order (e.g., ordering by error<br>injection type is not required).|
|ERRI-4|The host shall clear any unused entries in the Error Injection data structure to zero and the<br>device shall ignore all zeroed entries. The device shall check at least the first four bytes of<br>each Error Injection Entry data structure to determine if it is zeroed.|
|ERRI-5|The device shall abort the Error Injection Set Features command if the request contains an<br>error injection type that is not supported or the Single Instance value for the given Error<br>Injection Type is not valid.|
|ERRI-6|Once the trigger conditions specified in an Error Injection Entry are met, the device shall<br>inject the defined error event such that the host can detect the error through either an<br>AEN being sent, the CFS bit being set, or command being aborted. The device is not<br>required to cause the injected error to occur (e.g., injecting an Incomplete Shutdown error<br>requires the device to behave as if an Incomplete Shutdown occurred, but does not<br>require the device to perform an Incomplete Shutdown).|
|ERRI-7|If the single command injects multiple errors, then the errors may be injected in any order.<br>Error occurrence shall be based on the number of reads required to trigger each event.|

<!-- page 130 -->
**4.15.3.1** **Error Injection Entry Data Structure**

|Bit|Bit Description|
|---|---|
|7:2|Reserved.  Shall be cleared to zero.|
|1|Single Instance: If cleared to 0b, indicates error<br>injection is enabled until disabled.  If set to 1b,<br>indicates a single instance error injection<br>where a single error shall be injected.|
|0|Error Injection Enable: If cleared to 0b,<br>indicates error injection is disabled.  If set to<br>1b, indicates error injection is enabled.|

|Value|Description|
|---|---|
|0000h|Reserved.|
|0001h|CPU/Controller Hang|
|0002h|NAND Hang|
|0003h|PLP Defect|
|0004h|Logical Firmware Error|
|0005h|DRAM Corruption Critical Path|
|0006h|DRAM Corruption Non-Critical Path|
|0007h|NAND Corruption|
|0008h|SRAM Corruption|
|0009h|HW Malfunction|
|000Ah|No More NAND Spares Available|
|000Bh|Incomplete Shutdown|
|000Ch|Metadata Corruption|
|000Dh|Critical Garbage Collection|
|000Eh|Latency Spike|
|000Fh|I/O command failure|
|0010h|I/O command timeout|
|0011h|Admin command failure|
|0012h|Admin command timeout|
|0013h|Thermal Throttle Engaged|
|0014h|Thermal Throttle Disengaged|
|0015h|Critical Temperature Event|
|0016h|Die Offline|
|0017h -<br>FFFFh|Reserved.  Shall be cleared to zero.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|ERRIE-1|0|Error Entry<br>Flags|1|Error Entry Flags definition:<br>**Bit**<br>**Bit Description**<br>7:2 Reserved.  Shall be cleared to zero.<br>1 <br>Single Instance: If cleared to 0b, indicates error<br>injection is enabled until disabled.  If set to 1b,<br>indicates a single instance error injection<br>where a single error shall be injected.<br>0 <br>Error Injection Enable: If cleared to 0b,<br>indicates error injection is disabled.  If set to<br>1b, indicates error injection is enabled.|
|ERRIE-2|1|Reserved|1|Shall be cleared to zero.|
|ERRIE-3|3:2|Error Injection<br>Type|2|Error Injection type definition:<br>**Value**<br>**Description**<br>0000h<br>Reserved.<br>0001h<br>CPU/Controller Hang<br>0002h<br>NAND Hang<br>0003h<br>PLP Defect<br>0004h<br>Logical Firmware Error<br>0005h<br>DRAM Corruption Critical Path<br>0006h<br>DRAM Corruption Non-Critical Path<br>0007h<br>NAND Corruption<br>0008h<br>SRAM Corruption<br>0009h<br>HW Malfunction<br>000Ah<br>No More NAND Spares Available<br>000Bh<br>Incomplete Shutdown<br>000Ch<br>Metadata Corruption<br>000Dh<br>Critical Garbage Collection<br>000Eh<br>Latency Spike<br>000Fh<br>I/O command failure<br>0010h<br>I/O command timeout<br>0011h<br>Admin command failure<br>0012h <br>Admin command timeout <br>0013h<br>Thermal Throttle Engaged<br>0014h<br>Thermal Throttle Disengaged<br>0015h<br>Critical Temperature Event<br>0016h<br>Die Offline<br>0017h -<br>FFFFh<br>Reserved.  Shall be cleared to zero.|
|ERRIE-4|31:4|Error Injection<br>Type Specific<br>Definition|28|Error Injection Type specific definition.|

<!-- page 131 -->
**4.15.3.2** **Device Panic Error Injection Type**

The device shall inject a device panic that the host can detect through either an AEN or the CFS bit being
set. For the Device Panic type, a Single Instance value of 0 is not valid. Host shall perform the Panic Reset
and Device Recovery actions specified in Error Recovery (Log Identifier C1h).

|Bit|Bit Description|
|---|---|
|7:2|Reserved.  Shall be cleared to zero.|
|1|Shall be set to 1b.|
|0|Shall be set to 1b.|

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|ERRIEDP-1|0|Error Entry<br>Flags|1|Device Panic Error Entry Flags:<br>**Bit**<br>**Bit Description**<br>7:2<br>Reserved. Shall be cleared to zero.<br>1 <br>Shall be set to 1b.<br>0 <br>Shall be set to 1b.|
|ERRIEDP-2|1|Reserved|1|Shall be cleared to zero.|
|ERRIEDP-3|3:2|Error Injection<br>Type|2|Shall be set to the range of 0001h to 000Bh.|
|ERRIEDP-4|31:4|Error Injection<br>Type Specific<br>Definition|28|Device Panic Error Injection information:<br>**Byte**<br>**Address**<br>**Byte Description**<br>31:6<br>Reserved. Shall be cleared to zero.<br>5:4<br>Number of Reads to Trigger Device Panic<br>(NRTDP): Indicates the number of Read<br>commands the device shall process and<br>complete before triggering a device<br>panic.|

|Byte<br>Address|Byte Description|
|---|---|
|31:6|Reserved. Shall be cleared to zero.|
|5:4|Number of Reads to Trigger Device Panic<br>(NRTDP): Indicates the number of Read<br>commands the device shall process and<br>complete before triggering a device<br>panic.|

**4.15.4 Error Injection (Feature Identifier C0h) Get Features**

This Get Features returns the set of error injections that are enabled on the device, GETF-4 specifies the
acceptable values of the NSID field in the Get Features command. The attributes specified in Section
4.15.3.2 - Device Panic Error Injection Type are returned in Dword 0 of the completion queue entry and
the Error Inject data structure specified in Section 4.15.3.1 - Error Injection Entry Data Structure is
returned for each error injection in the data buffer for that command. If there are no currently enabled
error injections, the data buffer returned shall contain all zeroes. The device shall clear to zero all unused
entries in the Error Injection data structure.

**4.15.4.1** **Error Injection – Get Features Completion Queue Entry Dword 0**

|Requirement<br>ID|Field|Bits|Field Description|
|---|---|---|---|
|GERRI-1|Reserved|31:7|Shall be cleared to zero.|
|GERRI-2|Number of Error<br>Injections<br>(NUME)|6:0|This field indicates the number of outstanding enabled error<br>injections returned in the command data buffer (seeSection<br>4.15.3.1 Error Injection Entry Data Structure for the format of the<br>entries).|

<!-- page 132 -->
**4.15.5 PLP Failure Mode (Feature Identifier C2h) Set Features**

This Set Features defines the mode to which the device shall transition to on failure of the Power Loss
Protection (PLP) circuitry.

|Requirement ID|Description|
|---|---|
|ROWTM-1|The device shall default from the factory to Read Only Mode (ROM) (01b).|

|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SROWTM-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base Specification.|
|SROWTM-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|SROWTM-3|0|Reserved|13:10|Shall be cleared to zero.|
|SROWTM-4|0|Fused<br>Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|SROWTM-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|SROWTM-6|1|Namespace<br>Identifier<br>(NSID)|31:0|SeeGETF-4.|
|SROWTM-7|3:2|Reserved|All|Shall be cleared to zero.|
|SROWTM-8|5:4|Metadata<br>Pointer (MPTR)|All|Shall be cleared to zero.|
|SROWTM-9|9:6|Data Pointer<br>(DPTR)|All|Shall be cleared to zero.|
|SROWTM-10|10|Save (SV)|31|This bit specifies that the controller shall save the End-of-<br>Life Behavior state so that the state persists through all<br>power states and resets. The device shall support setting<br>this bit to 1b.|
|SROWTM-11|10|Reserved|30:8|Shall be cleared to zero.|
|SROWTM-12|10|Feature<br>Identifier (FID)|7:0|Shall be set to C2h.|

<!-- page 133 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SROWTM-13|11|End of Life<br>Behavior|31:30|Field to indicate device write behavior at End of Life (EOL)<br>or in the event of loss of PLP functionality. SeeEOL-5 for<br>definition on EOL.<br>**Value**<br>**Description**<br>00b<br>Reserved.<br>01b<br>The device shall transition to Read Only Mode<br>(ROM) in the event of PLP failure or at EOL.<br>10b<br>The device shall transition to Write Through<br>Mode (WTM) in the event of PLP failure and<br>transition to Read Only Mode (ROM) at EOL.<br>11b<br>The device shall continue to operate as normal<br>in the event of PLP failure and transition to<br>Read Only Mode (ROM) at EOL where EOL is<br>defined as the device no longer has enough<br>spare blocks to support Write commands.|
|SROWTM-14|11|Reserved|29:0|Shall be cleared to zero.|
|SROWTM-15|13:12|Reserved|All|Shall be cleared to zero.|
|SROWTM-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|SROWTM-17|15|Reserved|31:0|Shall be cleared to zero.|

|Value|Description|
|---|---|
|00b|Reserved.|
|01b|The device shall transition to Read Only Mode<br>(ROM) in the event of PLP failure or at EOL.|
|10b|The device shall transition to Write Through<br>Mode (WTM) in the event of PLP failure and<br>transition to Read Only Mode (ROM) at EOL.|
|11b|The device shall continue to operate as normal<br>in the event of PLP failure and transition to<br>Read Only Mode (ROM) at EOL where EOL is<br>defined as the device no longer has enough<br>spare blocks to support Write commands.|

**4.15.6 PLP Failure Mode (Feature Identifier C2h) Get Features**

GETF-4 specifies the acceptable values of the NSID field in the Get Features command. Dword 0 of
command completion queue entry.

|Requirement<br>ID|Field|Bits|Field Description|
|---|---|---|---|
|GROWTM-1|Reserved|31:3|Shall be cleared to zero.|

<!-- page 134 -->
|Value|Description|
|---|---|
|001b|The device will transition to Read Only Mode (ROM) in<br>the event of PLP failure or at EOL.|
|010b|The device will transition to Write Through Mode<br>(WTM) in the event of PLP failure and transition to<br>Read Only Mode (ROM) at EOL.|
|011b|The device will continue to operate as normal in the<br>event of PLP failure and transition to Read Only Mode<br>(ROM) at EOL.|

|Value|Description|
|---|---|
|001b|Read Only Mode (ROM) is the factory default.|
|010b|The Write Through Mode (WTM) is the factory default.|
|011b|Normal operation is the factory default for PLP failure.<br>Read Only Mode (ROM) is the factory default at EOL.|

|Value|Description|
|---|---|
|001b|The saved state is Read Only Mode (ROM).|
|010b|The saved state is Write Through Mode (WTM).|
|011b|The saved state is to operate as normal in the event of<br>PLP failure and Read Only Mode (ROM) at EOL.|

|Requirement<br>ID|Field|Bits|Field Description|
|---|---|---|---|
|GROWTM-2|End of Life<br>Behavior|2:0|Field to indicate what the device write behavior is configured for at End<br>of Life (EOL) or in the event of loss of PLP functionality.  The following<br>tables define the required return values for each Selection (SEL) state.<br>All other bit values are reserved.<br>Current state (Selection (SEL) cleared to 00b):<br>**Value**<br>**Description**<br>001b<br>The device will transition to Read Only Mode (ROM) in<br>the event of PLP failure or at EOL.<br>010b<br>The device will transition to Write Through Mode<br>(WTM) in the event of PLP failure and transition to<br>Read Only Mode (ROM) at EOL.<br>011b<br>The device will continue to operate as normal in the<br>event of PLP failure and transition to Read Only Mode<br>(ROM) at EOL.<br>Default state (Selection (SEL) set to 01b):<br>**Value**<br>**Description**<br>001b<br>Read Only Mode (ROM) is the factory default.<br>010b<br>The Write Through Mode (WTM) is the factory default.<br>011b<br>Normal operation is the factory default for PLP failure.<br>Read Only Mode (ROM) is the factory default at EOL.<br>Saved state (Selection (SEL) set to 10b):<br>**Value**<br>**Description**<br>001b<br>The saved state is Read Only Mode (ROM).<br>010b<br>The saved state is Write Through Mode (WTM).<br>011b<br>The saved state is to operate as normal in the event of<br>PLP failure and Read Only Mode (ROM) at EOL.<br>Capabilities (Selection (SEL) set to 11b):<br>**Value**<br>**Description**<br>101b<br>This feature is saveable, changeable, and not<br>namespace specific.|

|Value|Description|
|---|---|
|101b|This feature is saveable, changeable, and not<br>namespace specific.|

**4.15.7 Clear PCIe Correctable Error Counters (Feature Identifier C3h) Set Features**

|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|CPCIE-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base<br>Specification.|

<!-- page 135 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|CPCIE-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|CPCIE-3|0|Reserved|13:10|Shall be cleared to zero.|
|CPCIE-4|0|Fused Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|CPCIE-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|CPCIE-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|CPCIE-7|3:2|Reserved|All|Shall be cleared to zero.|
|CPCIE-8|5:4|Metadata<br>Pointer (MPTR)|All|Shall be cleared to zero.|
|CPCIE-9|9:6|Data Pointer<br>(DPTR)|All|Shall be cleared to zero.|
|CPCIE-10|10|Save (SV)|31|The device shall not support setting this bit to 1b.  If the<br>controller receives this Set Features command with the<br>bit set to 1b, then the device shall abort the command<br>with a status of Feature Identifier Not Saveable.|
|CPCIE-11|10|Reserved|30:8|Shall be cleared to zero.|
|CPCIE-12|10|Feature<br>Identifier (FID)|7:0|Shall be set to C3h.|
|CPCIE-13|11|Clear PCIe Error<br>Counters|31|Set to 1b to clear all PCIe correctable error counters in<br>the SMART / Health Information Extended log page (Log<br>Identifier C0h).<br>The nvme-cli plugin command “clear-pcie-correctable-<br>errors” can also perform this operation.|
|CPCIE-14|11|Reserved|30:0|Shall be cleared to zero.|
|CPCIE-15|13:12|Reserved|All|Shall be cleared to zero.|
|CPCIE-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|CPCIE-17|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.8 Clear PCIe Correctable Error Counters (Feature Identifier C3h) Get Features**

A Get Features command for Feature Identifier C3h should not be issued because no useful information is
returned. GETF-4 specifies the acceptable values of the NSID field in a Get Features command.

|Requirement ID|Description|
|---|---|
|GPCIE-1|The device shall clear Dword 0 of the completion queue entry to zero.|

**4.15.9 Enable IEEE1667 Silo (Feature Identifier C4h) Set Features**

This Set Features shall return an error if the OPAL Security state is not Manufactured Inactive.

<!-- page 136 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|S1667-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base<br>Specification.|
|S1667-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|S1667-3|0|Reserved|13:10|Shall be cleared to zero.|
|S1667-4|0|Fused Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|S1667-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|S1667-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|S1667-7|3:2|Reserved|All|Shall be cleared to zero.|
|S1667-8|5:4|Metadata<br>Pointer (MPTR)|All|Shall be cleared to zero.|
|S1667-9|9:6|Data Pointer<br>(DPTR)|All|Shall be cleared to zero.|
|S1667-10|10|Save (SV)|31|This bit specifies that the controller shall save the<br>IEEE1667 Silo Enable/Disable state so that the state<br>persists through all power states and resets. The device<br>shall support setting this bit to 1b.|
|S1667-11|10|Reserved|30:8|Shall be cleared to zero.|
|S1667-12|10|Feature<br>Identifier (FID)|7:0|Shall be set to C4h.|
|S1667-13|11|Enable IEEE1667<br>Silo|31|If set to 0b, the IEEE1667 silo shall be disabled no later<br>than the next power cycle. If set to 1b, the IEEE1667<br>silo shall be enabled no later than the next power cycle.|
|S1667-14|11|Reserved|30:0|Shall be cleared to zero.|
|S1667-15|13:12|Reserved|All|Shall be cleared to zero.|
|S1667-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|S1667-17|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.10 Enable IEEE1667 Silo (Feature Identifier C4h) Get Features**

GETF-4 specifies the acceptable values of the NSID field in the Get Features command. Dword 0 of
command completion queue entry.

|Requirement<br>ID|Field|Bits|Field description|
|---|---|---|---|
|G1667-1|Reserved|31:3|Shall be cleared to zero.|

<!-- page 137 -->
|Value|Description|
|---|---|
|000b|The IEEE1667 silo is currently disabled.|
|001b|The IEEE1667 silo is currently enabled.|

|Value|Description|
|---|---|
|000b|The IEEE1667 silo factory default is disabled.  Unless<br>otherwise specified, the device shall set the default<br>value of the IEEE1667 silo to 000b (disabled).|
|001b|The IEEE1667 silo factory default is enabled.|

|Value|Description|
|---|---|
|000b|The IEEE1667 silo saved state is disabled.|
|001b|The IEEE1667 silo saved state is enabled.|

|Requirement<br>ID|Field|Bits|Field description|
|---|---|---|---|
|G1667-2|IEEE1667<br>Silo Enabled|2:0|The following tables define the required return values for each<br>Selection (SEL) state.  All other values are illegal.<br>Current state (Selection (SEL) cleared to 00b):<br>**Value**<br>**Description**<br>000b<br>The IEEE1667 silo is currently disabled.<br>001b<br>The IEEE1667 silo is currently enabled.<br>Default state (Selection (SEL) set to 01b):<br>**Value**<br>**Description**<br>000b<br>The IEEE1667 silo factory default is disabled.  Unless<br>otherwise specified, the device shall set the default<br>value of the IEEE1667 silo to 000b (disabled).<br>001b<br>The IEEE1667 silo factory default is enabled.<br>Saved state (Selection (SEL) set to 10b):<br>**Value**<br>**Description**<br>000b<br>The IEEE1667 silo saved state is disabled.<br>001b<br>The IEEE1667 silo saved state is enabled.<br>Capabilities (Selection (SEL) set to 11b):<br>**Value**<br>**Description**<br>101b<br>This feature is saveable, changeable, and not namespace<br>specific.|

|Value|Description|
|---|---|
|101b|This feature is saveable, changeable, and not namespace<br>specific.|

**4.15.11 Latency Monitor (Feature Identifier C5h) Set Features**

This configures the Latency Monitor Feature.

|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|LMSF-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base<br>Specification.|
|LMSF-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|LMSF-3|0|Reserved|13:10|Shall be cleared to zero.|
|LMSF-4|0|Fused Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|LMSF-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|LMSF-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|LMSF-7|3:2|Reserved|All|Shall be cleared to zero.|

<!-- page 138 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|LMSF-8|5:4|Metadata<br>Pointer (MPTR)|All|Shall be cleared to zero.|
|LMSF-9|9:6|Data Pointer<br>(DPTR)|All|Shall contain one PRP that specifies a physically<br>contiguous 4096-byte address range that is 4096-byte<br>aligned (seeSection 4.15.11.1 Latency Monitoring Data<br>Structure Entry).|
|LMSF-10|10|Save (SV)|31|This bit specifies that the controller shall save the data<br>pointed to by the Data Pointer in LMSF-9 (Data Pointer<br>(DPTR)) so that the data persists through all power states<br>and resets. The device shall support setting this bit to<br>1b.|
|LMSF-11|10|Reserved|30:8|Shall be cleared to zero.|
|LMSF-12|10|Feature<br>Identifier (FID)|7:0|Shall be set to C5h.|
|LMSF-13|11|Reserved|31:0|Shall be cleared to zero.|
|LMSF-14|12:13|Reserved|All|Shall be cleared to zero.|
|LMSF-15|14|UUID Index|31:0|Shall be set perUUID-3.|
|LMSF-16|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.11.1** **Latency Monitoring Data Structure Entry**

This data structure is 4096 bytes with the following functional requirements and field format:

|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|
|---|---|---|---|---|
|LMDS-1|1:0|Active Bucket<br>Timer<br>Threshold|2|This is the value that loads the Active Bucket Timer<br>Threshold.|
|LMDS-2|2|Active<br>Threshold A|1|This is the value that loads into the Active Threshold A|
|LMDS-3|3|Active<br>Threshold B|1|This is the value that loads into the Active Threshold B|
|LMDS-4|4|Active<br>Threshold C|1|This is the value that loads into the Active Threshold C|
|LMDS-5|5|Active<br>Threshold D|1|This is the value that loads into the Active Threshold D|
|LMDS-6|7:6|Active<br>Latency<br>Config.|2|This is the value that loads into the Active Latency<br>Configuration.<br>|
|LMDS-7|8|Active<br>Latency<br>Minimum<br>Window|1|This is the value that loads into the Active Latency<br>Minimum Window.|

<!-- page 139 -->
|Requirement<br>ID|Byte<br>Address|Field|# of<br>Bytes|Field Description|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|LMDS-8|10:9|Debug Log<br>Trigger<br>Enable|2|This is the value that loads into the Debug Log Trigger<br>Enable.|This is the value that loads into the Debug Log Trigger<br>Enable.|This is the value that loads into the Debug Log Trigger<br>Enable.|This is the value that loads into the Debug Log Trigger<br>Enable.|
|LMDS-9|11|Discard<br>Debug Log|1||**Value**|**Description**||
|LMDS-9|11|Discard<br>Debug Log|1||00h|When cleared to 00h the debug log, if it<br>exists, will not be cleared.|When cleared to 00h the debug log, if it<br>exists, will not be cleared.|
|LMDS-9|11|Discard<br>Debug Log|1||01h|When set to 01h the debug log will be<br>discarded so another log can be triggered.<br>In addition to this, all the fields in the Set<br>Features Data structure are valid, which will<br>cause the Latency Monitor feature to be reset<br>and loaded with the values from the Set<br>Features command.<br>This shall discard the Debug Log regardless of<br>whether the Latency Monitoring Feature is<br>enabled or disabled.|When set to 01h the debug log will be<br>discarded so another log can be triggered.<br>In addition to this, all the fields in the Set<br>Features Data structure are valid, which will<br>cause the Latency Monitor feature to be reset<br>and loaded with the values from the Set<br>Features command.<br>This shall discard the Debug Log regardless of<br>whether the Latency Monitoring Feature is<br>enabled or disabled.|
|LMDS-9|11|Discard<br>Debug Log|1||02h|When set to 02h the debug log will be<br>discarded so another log can be triggered.<br>In addition to this none of the other fields of<br>the Set Features Data structure are valid.<br>Thus, only the debug log is discarded, and the<br>Latency Monitor feature is not reset or loaded<br>with any new values from the Set Features<br>command.<br>This shall discard the Debug Log regardless of<br>whether the Latency Monitoring Feature is<br>enabled or disabled.|When set to 02h the debug log will be<br>discarded so another log can be triggered.<br>In addition to this none of the other fields of<br>the Set Features Data structure are valid.<br>Thus, only the debug log is discarded, and the<br>Latency Monitor feature is not reset or loaded<br>with any new values from the Set Features<br>command.<br>This shall discard the Debug Log regardless of<br>whether the Latency Monitoring Feature is<br>enabled or disabled.|
|LMDS-9|11|Discard<br>Debug Log|1||03h -<br>FFh|Reserved. Shall be cleared to zero.|Reserved. Shall be cleared to zero.|
|LMDS-10|12|Latency<br>Monitor<br>Feature<br>Enable|1|When set to 01h the Latency Monitor Feature is enabled.<br>When cleared to 00h the Latency Monitor Feature is<br>disabled. All other values are reserved.|When set to 01h the Latency Monitor Feature is enabled.<br>When cleared to 00h the Latency Monitor Feature is<br>disabled. All other values are reserved.|When set to 01h the Latency Monitor Feature is enabled.<br>When cleared to 00h the Latency Monitor Feature is<br>disabled. All other values are reserved.|When set to 01h the Latency Monitor Feature is enabled.<br>When cleared to 00h the Latency Monitor Feature is<br>disabled. All other values are reserved.|
|LMDS-11|4095:13|Reserved|4083|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|Shall be cleared to zero.|

**4.15.12 Latency Monitor (Feature Identifier C5h) Get Features**

A Get Features command for Feature Identifier C5h should not be issued because no useful information is
returned. GETF-4 specifies the acceptable values of the NSID field in a Get Features command.

|Requirement ID|Description|
|---|---|
|LMGF-1|The device shall clear Dword 0 of the completion queue entry to zero.|

<!-- page 140 -->
**4.15.13 PLP Health Check Interval (Feature Identifier C6h) Set Features**

This Set Features defines the test interval that the device shall use to test that its Power Loss Protection
(PLP) circuitry is healthy.

|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SPLPI-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base<br>Specification.|
|SPLPI-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|SPLPI-3|0|Reserved|13:10|Shall be cleared to zero.|
|SPLPI-4|0|Fused Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|SPLPI-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|SPLPI-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|SPLPI-7|3:2|Reserved|All|Shall be cleared to zero.|
|SPLPI-8|5:4|Metadata<br>Pointer (MPTR)|All|Shall be cleared to zero.|
|SPLPI-9|9:6|Data Pointer<br>(DPTR)|All|Shall be cleared to zero.|
|SPLPI-10|10|Save (SV)|31|This bit specifies that the controller shall save the PLP<br>Health Check Interval so that the time interval persists<br>through all power states and resets. The device shall<br>support setting this bit to 1b.|
|SPLPI-11|10|Reserved|30:8|Shall be cleared to zero.|
|SPLPI-12|10|Feature<br>Identifier (FID)|7:0|Shall be set to C6h.|
|SPLPI-13|11|PLP Health Check<br>Interval|31:16|The time interval between PLP health checks in<br>minutes. If cleared to 0000h, then the health check is<br>disabled.|
|SPLPI-14|11|Reserved|15:0|Shall be cleared to zero.|
|SPLPI-15|13:12|Reserved|All|Shall be cleared to zero.|
|SPLPI-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|SPLPI-17|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.14 PLP Health Check Interval (Feature Identifier C6h) Get Features**

GETF-4 specifies the acceptable values of the NSID field in the Get Features command. Dword 0 of
command completion queue entry.

|Requirement<br>ID|Field|Bits|Field description|
|---|---|---|---|
|GPLPI-1|Reserved|31:16|Shall be cleared to zero.|

<!-- page 141 -->
|Value|Description|
|---|---|
|0000h|The PLP Health Check is currently disabled.|
|xxxxh|The PLP Health Check Interval is currently xxxxh<br>minutes.|

|Value|Description|
|---|---|
|0000h|The PLP Health Check Interval factory default is<br>disabled.|
|000Fh|The PLP Health Check Interval factory default is<br>000Fh minutes.|

|Value|Description|
|---|---|
|0000h|The PLP Health Check Interval saved state is<br>disabled.|
|xxxxh|The PLP Health Check Interval saved state is<br>xxxxh minutes.|

|Requirement<br>ID|Field|Bits|Field description|
|---|---|---|---|
|GPLPI-2|PLP<br>Health<br>Check<br>Interval|15:0|The following tables define the required return values for each<br>Selection (SEL) state.  All other values are illegal.<br>Current state (Selection (SEL) cleared to 00b):<br>**Value**<br>**Description**<br>0000h<br>The PLP Health Check is currently disabled.<br>xxxxh<br>The PLP Health Check Interval is currently xxxxh<br>minutes.<br>Default state (Selection (SEL) set to 01b):<br>**Value**<br>**Description**<br>0000h<br>The PLP Health Check Interval factory default is<br>disabled.<br>000Fh<br>The PLP Health Check Interval factory default is<br>000Fh minutes.<br>Saved state (Selection (SEL) set to 10b):<br>**Value**<br>**Description**<br>0000h<br>The PLP Health Check Interval saved state is<br>disabled.<br>xxxxh<br>The PLP Health Check Interval saved state is<br>xxxxh minutes.<br>Capabilities (Selection (SEL) set to 11b):<br>**Value**<br>**Description**<br>0005h<br>This feature is saveable, changeable, and not<br>namespace specific.|

|Value|Description|
|---|---|
|0005h|This feature is saveable, changeable, and not<br>namespace specific.|

**4.15.15 DSSD Power State (Feature Identifier C7h) Set Features**

|Requirement ID|Description|
|---|---|
|DSSDPSS-1|If the host selects an DSSD Power State via a DSSD Power State (Feature Identifier C7h) Set<br>Feature, the device shall accept the command and run at the highest powered NVMe<br>Power State whose Maximum Power (MP) is less than or equal to the number of the DSSD<br>Power State in watts (seeDCLP-9 andDSSDPSD-3).|
|DSSDPSS-2|<br>If the host selects a DSSD Power State via DSSD Power State (Feature Identifier C7h) Set<br>Features and the number of that DSSD Power State is less than the Minimum DSSD Power<br>State (seeDCLP-8), the device shall abort the Set Features command with Invalid Field in<br>Command status.|

This Set Features causes the device to move to the given DSSD Power State:

<!-- page 142 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SDSSDPS-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base<br>Specification.|
|SDSSDPS-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|SDSSDPS-3|0|Reserved|13:10|Shall be cleared to zero.|
|SDSSDPS-4|0|Fused Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|SDSSDPS-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|SDSSDPS-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|SDSSDPS-7|3:2|Reserved|All|Shall be cleared to zero.|
|SDSSDPS-8|5:4|Metadata Pointer<br>(MPTR)|All|Shall be cleared to zero.|
|SDSSDPS-9|9:6|Data Pointer<br>(DPTR)|All|Shall be cleared to zero.|
|SDSSDPS-10|10|Save (SV)|31|This bit specifies that the controller shall persist the<br>DSSD Power State through all power cycles and resets.<br>The device shall support setting this bit to 1b.|
|SDSSDPS-11|10|Reserved|30:8|Shall be cleared to zero.|
|SDSSDPS-12|10|Feature Identifier<br>(FID)|7:0|Shall be set to C7h.|
|SDSSDPS-13|11|Reserved|31:7|Shall be cleared to zero.|
|SDSSDPS-14|11|DSSD Power State|6:0|DSSD Power State to set in watts.|
|SDSSDPS-15|13:12|Reserved|All|Shall be cleared to zero.|
|SDSSDPS-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|SDSSDPS-17|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.16 DSSD Power State (Feature Identifier C7h) Get Features**

|Requirement ID|Description|
|---|---|
|DSSDPSG-1|If a DSSD Power State (Feature Identifier C7h) Get Features command is executed and the<br>current NVMe Power State was selected because of a DSSD Power State Set Features<br>command, the device shall report the DSSD Power State selected by that command (see<br>Section 4.8.11 DSSD Power State Requirements for an example).|
|DSSDPSG-2|If a DSSD Power State (Feature Identifier C7h) Get Features command is executed and the<br>current NVMe Power State was not selected because of a DSSD Power State Set Features<br>command, the device shall report the lowest power DSSD Power State whose number is<br>greater than or equal to the Maximum Power in watts of the current NVMe Power State<br>(seeSection 4.8.11 DSSD Power State Requirements for an example).|

GETF-4 specifies the acceptable values of the NSID field in the Get Features command. Dword 0 of
command completion queue entry.

<!-- page 143 -->
|Value|Description|
|---|---|
|xx|The DSSD Power State is currently xx watts as<br>specified byDSSDPSG-1 andDSSDPSG-2.|

|Value|Description|
|---|---|
|xx|The DSSD Power State factory default is xx watts.|

|Value|Description|
|---|---|
|xx|The DSSD Power State saved state is xx watts.|

|Requirement<br>ID|Field|Bits|Field Description|
|---|---|---|---|
|GDSSDPS-1|Reserved|31:7|Shall be cleared to zero.|
|GDSSDPS-2|DSSD Power<br>State|6:0|The following tables define the required return values for each<br>Selection (SEL) state.  All other values are illegal.<br>Current state (Selection (SEL) cleared to 00b):<br>**Value**<br>**Description**<br>xx<br>The DSSD Power State is currently xx watts as<br>specified byDSSDPSG-1 andDSSDPSG-2. <br>Default state (Selection (SEL) set to 01b):<br>**Value**<br>**Description**<br>xx<br>The DSSD Power State factory default is xx watts.<br>Saved state (Selection (SEL) set to 10b):<br>**Value**<br>**Description**<br>xx<br>The DSSD Power State saved state is xx watts.<br>Capabilities (Selection (SEL) set to 11b):<br>**Value**<br>**Description**<br>0005h<br>This feature is saveable, changeable, and not<br>namespace specific.|

|Value|Description|
|---|---|
|0005h|This feature is saveable, changeable, and not<br>namespace specific.|

**4.15.17 Telemetry Profile (Feature Identifier C8h) Set Features**

**4.15.17.1 Telemetry Profiles**

Telemetry profiles enable the following to be configured:

- Data Area 1 Last Block

- Data Area 2 Last Block

- Statistic Area Location and Size

- Event FIFO Start and End locations and number of Event FIFOs

In the Telemetry Controller-Initiated log page and Telemetry Host-Initiated log page there is the Number of
Telemetry Profiles Supported field. This field enables the device to report the number of Telemetry
Profiles supported. There is also a Telemetry Profile Selected field. This reports what profile is currently
selected. The Telemetry Profile Selected field can be changed through Set Features. The Telemetry
Controller-Initiated log page and Telemetry Host-Initiated log page can then be read to see the format of
the Telemetry Profile. Having different profiles enables the device to optimize debug for different
situations.

**4.15.17.2** **Telemetry Profile (Feature Identifier C8h) Set Features**

Set Features to set the Telemetry Profile.

<!-- page 144 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|TEL-CFG-SF-1|0|Command Identifier (CID)|31:16|Shall be set as defined in NVM Express Base<br>Specification.|
|TEL-CFG-SF-2|0|PRP or SGL for Data<br>Transfer (PSDT)|15:14|Shall be cleared to 00b to specify that PRPs<br>are used.|
|TEL-CFG-SF-3|0|Reserved|13:10|Shall be cleared to zero.|
|TEL-CFG-SF-4|0|Fused Operation (FUSE)|9:8|Shall be cleared to 00b.|
|TEL-CFG-SF-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|TEL-CFG-SF-6|1|Namespace Identifier<br>(NSID)|31:0|SeeGETF-4.|
|TEL-CFG-SF-7|3:2|Reserved|All|Shall be cleared to zero.|
|TEL-CFG-SF-8|5:4|Metadata Pointer (MPTR)|All|Shall be cleared to zero.|
|TEL-CFG-SF-9|9:6|Data Pointer (DPTR)|All|Shall be cleared to zero.|
|TEL-CFG-SF-10|10|Save (SV)|31|This bit shall be set to 1b.|
|TEL-CFG-SF-11|10|Reserved|30:8|Shall be cleared to zero.|
|TEL-CFG-SF-12|10|Feature Identifier (FID)|7:0|Shall be set to C8h.|
|TEL-CFG-SF-13|11|Reserved|31:8|Shall be cleared to zero.|
|TEL-CFG-SF-14|11|Telemetry Profile Select<br>(TPS)|7:0|The device shall collect debug data per the<br>specified profile number.|
|TEL-CFG-SF-15|13:12|Reserved|All|Shall be cleared to zero.|
|TEL-CFG-SF-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|TEL-CFG-SF-17|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.18 Telemetry Profile (Feature Identifier C8h) Get Features**

This Get Features returns the telemetry profile that is currently selected on the device, GETF-4 specifies the
acceptable values of the NSID field in a Get Features command. Dword 0 of command completion queue
entry.

|Requirement ID|Field|Bits|Description|
|---|---|---|---|
|TEL-CFG-GF-1|n/a|n/a|Obsolete.  SeeTEL-CFG-SF-2 andTEL-CFG-SF-3.|
|<br>TEL-CFG-GF-2|<br>Reserved|<br>31:8|<br>Shall be cleared to 0.|
|TEL-CFG-GF-3|Telemetry<br>Profile Select<br>(TPS)|7:0|This field indicates the currently selected telemetry profile (see<br>TEL-CFG-SF-14).|

**4.15.19 DSSD Asynchronous Event Configuration (Feature Identifier C9h) Set Features**

This Feature controls the DSSD events that cause an asynchronous event notification to be sent to the host.
If the condition for an event is true when the corresponding notice indicated in Command Dword 11 is
enabled and there’s an outstanding Asynchronous Event Request command, then that event is sent to the
host. If the notice indicated in Command Dword 11 is disabled, then that event is not sent to the host.

|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SDAEC-1|0|Command<br>Identifier (CID)|31:16|Shall be set as defined in NVM Express Base Specification.|

<!-- page 145 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SDAEC-2|0|PRP or SGL for<br>Data Transfer<br>(PSDT)|15:14|Shall be cleared to 00b to specify that PRPs are used.|
|SDAEC-3|0|Reserved|13:10|Shall be cleared to zero.|
|SDAEC-4|0|Fused<br>Operation<br>(FUSE)|9:8|Shall be cleared to 00b.|
|SDAEC-5|0|Opcode (OPC)|7:0|Shall be set to 09h.|
|SDAEC-6|1|Namespace<br>Identifier (NSID)|31:0|SeeGETF-4.|
|SDAEC-7|3:2|Reserved|All|Shall be cleared to zero.|
|SDAEC-8|5:4|Metadata<br>Pointer (MPTR)|All|Shall be cleared to zero.|
|SDAEC-9|9:6|Data Pointer<br>(DPTR)|All|Shall be cleared to zero.|
|SDAEC-10|10|Save (SV)|31|The device shall not support setting this bit to 1b. If the<br>controller receives this Set Features command with the<br>bit set to 1b, then the device shall abort the command<br>with a status of Feature Identifier Not Saveable.|
|SDAEC-11|10|Reserved|30:8|Shall be cleared to zero.|
|SDAEC-12|10|Feature<br>Identifier (FID)|7:0|Shall be set to C9h.|
|SDAEC-13|11|Reserved|31:1|Shall be cleared to zero.|

<!-- page 146 -->
|Requirement<br>ID|Dword|Field|Bits|Field Description|
|---|---|---|---|---|
|SDAEC-14|11|Enable Panic<br>AENs|0|This bit specifies whether an asynchronous event<br>notification is sent to the host for a panic event (see<br>EREC-5). <br>If this bit is set to 1b and there is an outstanding<br>Asynchronous Event Request command, then:<br>• <br>the Panic AEN is sent to the host when this condition<br>occurs unless the device is unable to generate<br>command completions; and<br>• <br>the Controller Fatal Status bit in the in-band<br>Controller Status property shall not be set to 1b when<br>a panic event occurs; however, the Controller Fatal<br>Status bit in the out-of-band Controller Health Data<br>Structure shall still be set to 1b.<br>If this bit is cleared to 0b, or the controller is unable to<br>complete a Panic AEN, then:<br>• <br>the Panic AEN shall not be sent to the host; and<br>• <br>the Controller Fatal Status bit in the in-band<br>Controller Status property and in the in-band and out-<br>of-band Controller Health Data Structure shall be set<br>to 1b when a panic event occurs.|
|SDAEC-15|13:12|Reserved|All|Shall be cleared to zero.|
|SDAEC-16|14|UUID Index|31:0|Shall be set perUUID-3.|
|SDAEC-17|15|Reserved|31:0|Shall be cleared to zero.|

**4.15.20 DSSD Asynchronous Event Configuration (Feature Identifier C9h) Get Features**

GETF-4 specifies the acceptable values of the NSID field in the Get Features command. Dword 0 of
command completion queue entry.

|Requirement<br>ID|Field|Bits|Field description|
|---|---|---|---|
|GDAEC-1|Reserved|31:1|Shall be cleared to zero.|
|GDAEC-2|Enable<br>Controller<br>Fatal Status<br>Notices|0|This bit indicates whether a Panic AEN is sent to the host for a panic<br>event (seeEREC-5). If this bit is set to 1b and there is an outstanding<br>Asynchronous Event Request command, then the Panic AEN is sent to<br>the host when this condition occurs. If this bit is cleared to 0b, then<br>the Panic AEN shall not be sent to the host.<br>The default value of this bit following a Controller Level Reset shall be<br>0b.|

<!-- page 147 -->
## **5 PCIe Requirements**

The following are PCIe requirements.

|Requirement ID|Description|
|---|---|
|PCI-1|The device shall support a PCIe Maximum Payload Size (MPS) of 512 bytes or larger. When<br>the device transmits data, the device shall use the largest MPS possible. Changes to the<br>MPS shall take effect immediately without requiring a Controller Reset or any other type of<br>reset.|
|PCI-2|The device shall support modification of PCIe TLP completion timeout range as defined by<br>the PCI Express Base Specification.|
|PCI-3|The vendor shall disclose the vendor-specific timeout range definition in the “Completion<br>Timeout Ranges Supported” field in the PCI Express Base Specification.|
|PCI-4|The device shall support disabling PCIe Completion Timeout.|
|PCI-5|The device shall perform a PCIe Fundamental Reset when PERST# is asserted, and main<br>power has not been removed even if firmware is hung.|
|PCI-6|PCIe Function Level Reset shall be supported.|
|PCI-7|Obsolete. See PCI-5.|
|PCI-8|The device shall not expose a BAR4 or a BAR5 if neither CMB nor PMR is supported.|
|PCI-9|The device shall support MSI-X.|
|PCI-10|The MSI-X table shall reside in BAR0.|
|PCI-11|If implemented, the MSI capability structure in configuration space shall be 4-byte aligned.|
|PCI-12|Any optional PCI features supported by the device not described in this document shall be<br>clearly documented and disclosed to the customer.|
|PCI-13|The device shall support Completion Timeout Ranges A, B and C.|
|PCI-14|The device shall support Relaxed Ordering.|
|PCI-15|The device shall not set the Relaxed Ordering bit in transactions it initiates as a Requester<br>that require strong ordering (i.e., transactions that would violate the NVMe protocol or<br>result in data corruption if re-ordered shall clear the Relaxed Ordering bit to 0b). For<br>example, the Enable Relaxed Ordering bit in transactions initiated by the device as a<br>Requester shall be cleared to 0b in MSI/MSI-X writes, writes to the Completion Queue<br>Entry, etc.|
|PCI-16|The device shall set the Relaxed Ordering bit in data DMAs, if Relaxed Ordering is enabled.|
|PCI-17|The device shall support all link speeds between the lowest link speed and the highest link<br>speed, inclusive (e.g., a device compliant with the PCI Express Base Specification Revision<br>5.0 Version 1.0 shall support link speeds of 2.5 GT/s, 5.0 GT/s, 8 GT/S, 16 GT/s, and<br>32 GT/s).|
|PCI-18|The device shall not require Device Specific Initialization (DSI).|
|PCI-19|The device shall not perform a soft reset when transitioning from D3hot to D0 (i.e.,<br>No_Soft_Reset bit in the Power Management Control/Status Register shall be set to 1b).|
|PCI-20|The device shall not support BARs that map to I/O Space.|
|PCI-21|All BARs that map to Memory Space shall be 64-bit capable (i.e., bits 2:1 of the BAR shall<br>be set to 10b) and shall support the full 64-bit address space.|
|PCI-22|The sum of the size of all BARs for a single non-SR-IOV function or SR-IOV Physical Function<br>that maps to Memory Space shall be less than or equal to 1 MiB if neither CMB nor PMR is<br>supported.|

<!-- page 148 -->
|Requirement ID|Description|
|---|---|
|PCI-23|The device shall require a max of one PCI bus number (e.g., no PCIe switches are allowed).|
|PCI-24|The device’s DMA engines shall support the full 64-bit address space with uniform<br>performance across the entire address range.|
|PCI-25|The Device Serial Number Extended Capability shall be supported except for virtual<br>functions. All functions on all ports of a device that implement this capability shall return<br>the same serial number value. The serial number shall be unique for each device and<br>independent from all other unique identifiers on the device (e.g., for namespaces,<br>controllers, etc.).|
|PCI-26|The device shall support the Advanced Error Reporting Extended Capability.|
|PCI-27|The device shall silently discard (following normal data link layer processing) without<br>logging or signaling an error, any PCIe VDMs targeting a Function while it is in Function<br>Level Reset (FLR). When an FLR is initiated for a Function, any already-received PCIe VDMs<br>still being processed by that Function shall be silently discarded.<br>This requirement prohibits non-silent-discard behavior during an FLR that is allowed by the<br>PCI Express Base Specification.|
|PCI-28|The device may support Address Translation Services (ATS).|
|PCI-29|While any one or more Functions on the device are in the D3hot power state, MCTP over<br>PCIe VDM processing shall be fully operational and the device shall not generate errors for<br>valid MCTP over PCIe VDMs received while in this state. For example, while in this state,<br>the device shall be able to successfully process MCTP over PCIe VDM requests, transmit<br>the response, and shall be able to transmit MCTP messages for any asynchronous events<br>that occur and are enabled.<br>This requirement applies to all supported MCTP message types (e.g., NVMe-MI, SPDM,<br>etc.).|
|PCI-30|PCIe non-Fundamental Resets (e.g., Function Level Reset, hot reset, or reset due to a link<br>down/link disabled condition) shall not clear the device’s captured PCIe bus number(s) or<br>MCTP Endpoint ID(s). This is required so that devices can continue to communicate via<br>MCTP over PCIe VDM following these types of resets without having to be re-initialized.<br>PCIe Fundamental Resets shall clear the captured PCIe bus number(s) as required by the<br>PCI Express Base Specification and shall clear the MCTP Endpoint ID(s) as required by the<br>MCTP PCIe Transport Binding Specification.|
|PCI-31|If an MCTP over PCIe VDM would otherwise signal Unsupported Request (e.g., ID Routed<br>Message targeting a Function that is not implemented) is received, then the device shall<br>silently discard that message.|
|PCI-32|In addition to responding to Broadcast from Root Complex as required by the MCTP PCIe<br>VDM Binding Specification, a PCIe VDM Management Endpoint shall respond to Route by<br>ID Message Requests for the following MCTP control messages:<br>• <br>Prepare for Endpoint Discovery; and<br>• <br>Endpoint Discovery.|

<!-- page 149 -->
|Requirement ID|Description|
|---|---|
|PCI-33|PERST# shall not be treated as a power cycle. For example, PERST#:<br>• <br>shall not cause TCG Opal devices to go to the Read Locked/Write Locked state (i.e.,<br>PERST# maps to the TCG reset type of Hardware Reset, not a Power Cycle, as defined<br>by the TCG Storage Interface Interactions Specification) if the host has not configured a<br>TCG HW Reset as one of the Reset Types that can lock the device’s locking ranges on<br>LockOnReset in addition to Power Cycle; and<br>• <br>shall not cause commands prohibited via the NVMe Lockdown command to be un-<br>prohibited.|
|PCI-34|PERST# shall not cause RW1CS bits defined by the PCI Express Base Specification (e.g., bits<br>in the Uncorrectable Error Status and Correctable Error Status registers) to be cleared.|
|PCI-35|The device shall not support either the D1 or the D2 power management states.|
|PCI-36|If any power-of-two-sized access, up to 8-bytes in size, to the memory pointed to by any of<br>the NVMe device's BARs (e.g., access to controller registers) is aligned to a power-of-two<br>boundary equal to the size of the access (e.g., a 2-byte access aligned to a 2-byte<br>boundary, a 4-byte access aligned to a 4-byte boundary, etc.), then the access shall not be<br>considered a restricted programming model violation (i.e., the access shall be processed<br>successfully unless some other error unrelated to a restricted programming model<br>violation is encountered).<br>Support is optional for any accesses greater than 8-bytes in size to the memory pointed to<br>by NVMe BAR0/BAR1 (e.g., access to controller registers). The restricted programming<br>model for the memory pointed to by BARs other than BAR0/BAR1 may support additional<br>access sizes as required by the device vendor.<br>For any access that results in a restricted programming model violation, the request shall<br>be handled as an Unsupported Request or Completer Abort as permitted for restricted<br>programming model violations as defined by the PCI Express Base Specification (e.g., the<br>device firmware shall not hang due to a restricted programming model violation).|
|PCI-37|If the device receives an MCTP over PCIe VDM that is invalid due to an MCTP base layer<br>error or MCTP message-type layer (e.g., NVMe-MI, SPDM) error, then the error shall be<br>reported, if possible, at the MCTP base layer or MCTP message-type layer respectively;<br>otherwise, the invalid MCTP over PCIe VDM shall be silently discarded.<br>This requirement applies to all supported MCTP message types (e.g., NVMe-MI, SPDM,<br>etc.).|
|PCI-38|A Function Level Reset to a Function other than the Function associated with the MCTP<br>endpoint shall have no impact on MCTP traffic on the Function associated with the MCTP<br>endpoint.|
|PCI-39|The device shall perform a PCIe Conventional Reset per the PCI Express Base Specification<br>(e.g., resetting PCIe-defined state machines, setting PCIe-defined registers to default, etc.)<br>when main power has not been removed and any of the following conditions occur, even if<br>the firmware is not functioning (e.g., has asserted or is otherwise non-responsive):<br>• <br>the PCIe link is disabled; or<br>• <br>the device is reset by a PCIe hot reset.|

<!-- page 150 -->
### **5.1 Boot Requirements**

|Requirement ID|Description|
|---|---|
|BOOT-1|The device shall support the UEFI 2.0 and all later versions of the Tianocore EDKII NVMe<br>driver.|
|BOOT-2|The device shall neither support nor include an option ROM.|

### **5.2 PCIe Error Logging**

The following table indicates where the PCIe physical layer error counters shall be logged.  This is in
addition to the aggregated PCIe error counters defined in SMART / Health Information Extended log page
(Log Identifier C0h).

|Requirement<br>ID|Event|Logging Mechanism|
|---|---|---|
|PCIERR-1|Unsupported Request Error Status (URES)|Uncorrectable Error Status Register Offset 04h<br>in PCI Express Base Specification.|
|PCIERR-2|ECRC Error Status (ECRCES)|ECRC Error Status (ECRCES)|
|PCIERR-3|Malformed TLP Status (MTS)|Malformed TLP Status (MTS)|
|PCIERR-4|Receiver Overflow Status (ROS)|Receiver Overflow Status (ROS)|
|PCIERR-5|Unexpected Completion Status (UCS)|Unexpected Completion Status (UCS)|
|PCIERR-6|Completer Abort Status (CAS)|Completer Abort Status (CAS)|
|PCIERR-7|Completion Timeout Status (CTS)|Completion Timeout Status (CTS)|
|PCIERR-8|Flow Control Protocol Error Status (FCPES)|Flow Control Protocol Error Status (FCPES)|
|PCIERR-9|Poisoned TLP Status (PTS)|Poisoned TLP Status (PTS)|
|PCIERR-10|Data Link Protocol Error Status (DLPES)|Data Link Protocol Error Status (DLPES)|
|PCIERR-11|Advisory Non-Fatal Error Status (ANFES)|Correctable Error Status Register Offset 10h in<br>PCI Express Base Specification.|
|PCIERR-12|Replay Timer Timeout Status (RTS)|PCIe Correctable Error Count in the SMART /<br>Health Information Extended log page (Log<br>Identifier C0h) (seeSMART-14).|
|PCIERR-13|REPLAY_NUM Rollover Status (RRS)|REPLAY_NUM Rollover Status (RRS)|
|PCIERR-14|Bad DLLP Status (BDS)|Bad DLLP Status (BDS)|
|PCIERR-15|Bad TLP Status (BTS)|Bad TLP Status (BTS)|
|<br>PCIERR-16|<br>Receiver Error Status (RES)|<br>Receiver Error Status (RES)|

### **5.3 Low Power Modes**

|Requirement ID|Description|
|---|---|
|LPWR-1|ASPM shall be disabled after a power cycle or PCIe resets as defined by the PCI Express<br>Base Specification.|
|LPWR-2|The device shall support the PCIe ASPM L1 power state.|

### **5.4 PCIe Eye Capture**

|Requirement ID|Description|
|---|---|
|EYE-1|A utility shall be provided that takes the entire Physical Interface Receiver Eye Opening<br>Measurement log page as an input and decodes the Eye Data field of each lane in the log<br>page.|

<!-- page 151 -->
## **6 Optional Device Features**

Features in this section are optional. If the feature is implemented, it shall follow the requirements in this
section.

### **6.1 Flexible Data Placement Requirements**

If Flexible Data Placement is supported, then the Generic Flexible Data Placement Requirements and a
minimum of one of the Flexible Data Placement configurations shall be supported:

**6.1.1 Generic Flexible Data Placement Requirements**

|Requirement ID|Description|
|---|---|
|FDPG-1|Obsolete (seeNVMe-OPT-16).|
|FDPG-2|It shall be clearly disclosed to the customer which FDP Event Types are supported and<br>what additional fields related to this are supported with each event type (FDP Event Flags,<br>PID, NSID, Reclaim Group Identifier, Reclaim Unit Handle Identifier, etc.)|

**6.1.2 FDP Single Reclaim Group Configuration**

|Requirement ID|Description|
|---|---|
|FDPSRG-1|The number of advertised reclaim groups (NRG) shall be 1.|
|FDPSRG-2|The device shall support a minimum of 8 reclaim unit handles.|
|FDPSRG-3|The device shall set Volatile Write Cache Present to 0b (not supported).|
|FDPSRG-4|The device shall support an FDP configuration with a minimum of 8 reclaim unit handles of<br>Reclaim Unit Handle Type Initially Isolated.|
|FDPSRG-5|The device shall support an FDP configuration with a minimum of 8 reclaim unit handles of<br>Reclaim Unit Handle Type Persistently Isolated.|
|FDPSRG-6|Single reclaim group configurations shall support a minimum of 8 namespaces.|
|FDPSRG-7|Single reclaim group configurations shall support multiple sector sizes in an FDP<br>configuration.|

**6.1.3 FDP Die Placement Configuration**

|Requirement ID|Description|
|---|---|
|FDPDP-1|The number of advertised reclaim groups (NRG) shall match the number of flash dies in the<br>NVM subsystem.|
|FDPDP-2|The configuration shall support a minimum of 8 reclaim unit handles. In other words, it<br>shall be possible to utilize (NRG) x 8 placement identifiers simultaneously.|

### **6.2 DIX Requirements**

If DIX is supported, then the following shall be supported:

<!-- page 152 -->
|Field|Value|
|---|---|
|PIL (Protection Information Location)|0b|
|PI (Protection Information)|011b (Type 3)|
|MSET (Metadata Settings)|0b (DIX)|
|LBAF (LBA Format)|4K+64*|
|LBAFEE (LBA Format Extension Enable)|0b|
|PRACT (Protection Information Action)|0b and 1b|
|PRCHK (Protection Information Check):  Guard Check (bit 2)|1b|
|PRCHK (Protection Information Check):  Application Tag Check (bit 1)|0b|
|PRCHK (Protection Information Check):  Reference Tag check (bit 0)|0b|
|STC (Storage Tag Check)|0b|

|Requirement ID|Description|
|---|---|
|DIX-1|The following DIX configuration shall be supported.<br>**Field**<br>**Value**<br>PIL (Protection Information Location)<br>0b<br>PI (Protection Information)<br>011b (Type 3)<br>MSET (Metadata Settings)<br>0b (DIX)<br>LBAF (LBA Format)<br>4K+64* <br>LBAFEE (LBA Format Extension Enable)<br>0b<br>PRACT (Protection Information Action)<br>0b and 1b<br>PRCHK (Protection Information Check):  Guard Check (bit 2)<br>1b<br>PRCHK (Protection Information Check):  Application Tag Check (bit 1)<br>0b<br>PRCHK (Protection Information Check):  Reference Tag check (bit 0)<br>0b<br>STC (Storage Tag Check)<br>0b<br>*4 KiB logical blocks, each of which has an additional 64 bytes of metadata.|

## **7 Reliability**

### **7.1 Uncorrectable Bit Error Rate**

|Requirement ID|Description|
|---|---|
|UBER-1|The device shall support an Uncorrectable Bit Error Rate (UBER) of < 1 sector per 1017 bits<br>read.|

### **7.2 Power On/Off Requirements**

**7.2.1 Time to Ready and Shutdown Requirements**

|Requirement ID|Description|
|---|---|
|TTR-1|The device shall be able to process the Identify command with a successful completion<br>within 1 second of CC.EN being set to 1b provided a Shutdown is not in progress when<br>CC.EN is set to 1b. Some models may allow a longer time (seeSection 13 Device Profiles).|
|TTR-2|<br>The device shall be able to process I/O and Admin commands that require access to media<br>with a successful completion within 20 seconds after CC.EN has been set to 1b. Some<br>models require a different time (seeSection 13 Device Profiles). SeeTTR-22 for additional<br>requirements for time to ready after PCIe Conventional Reset.|
|TTR-3|The device shall be able to process Admin commands with a successful completion as soon<br>as CSTS.RDY = 1. Slower processing of Admin commands that require media access is<br>acceptable while the media is becoming ready.|
|TTR-4|The device shall keep CSTS.RDY = 0 until the device is able to process Admin commands.<br>Some models may have additional requirements before CSTS.RDY can be set to 1 (see<br>Section 13 Device Profiles).|
|TTR-5|<br>The Shutdown Notification completion (i.e., the CSTS.SHST set to 10b) shall be received<br>within 10 seconds after the start of a normal shutdown (i.e., after CC.SHN is set to 01b).|
|TTR-6|The device shall support both the CC.SHN Normal and Abrupt Shutdown Notifications.|

<!-- page 153 -->
|Requirement ID|Description|
|---|---|
|TTR-7|After a normal shutdown is completed successfully, the device shall not enter a<br>rebuild/recovery mode on the next power on.|
|TTR-8|A normal shutdown shall trigger flushing to non-volatile memory of any content within the<br>device’s internal cache(s) (e.g., SRAM/DRAM), if present, which is required to be non-<br>volatile.|
|TTR-9|Obsolete. SeeNVMe-CFG-3.|
|TTR-10|Obsolete. Moved toPLP-1.|
|<br>TTR-11|<br>Obsolete. Moved toPLP-2.|
|TTR-12|Metadata rebuild due to any reason (e.g., unexpected power loss) shall not exceed 120<br>seconds and the device shall meet its latency requirements after this.|
|TTR-13|Obsolete. Moved toPLP-3.|
|TTR-14|Obsolete. Moved toPLP-4.|
|TTR-15|In case of a successful Normal shutdown operation (CC.SHN = 1 set by the NVMe device<br>driver), no data loss is tolerated even if PLP has failed.|
|TTR-16|Any shutdown event shall not make the device non-functional under any conditions.|
|TTR-17|Obsolete. Moved toPLP-5.|
|<br>TTR-18|<br>Obsolete. Moved toPLP-6.|
|<br>TTR-19|<br>When the CC.SHN register is written to notify the device to shut down it shall not be<br>assumed that power will be lost even after CC.EN is cleared to 0. Under these conditions<br>the device shall continue to function properly based on the NVMe and PCIe Specifications.|
|TTR-20|The device shall be able to successfully respond to Configuration space accesses within 1s<br>from de-assertion of PERST#.|
|TTR-21|All AENs defined by this specification required for supporting OCP requirements shall be<br>enabled when setting CSTS.RDY to 1b.|
|TTR-22|Upon completion of a PCIe Conventional Reset, the device shall start initializing the media<br>and within 20 seconds from the completion of the PCIe Conventional Reset shall be able to<br>successfully process:<br>• <br>in-band I/O and Admin commands requiring media access, assuming CC.EN has<br>been set to 1b; and<br>• <br>out-of-band Admin commands requiring media access, including prior to the in-<br>band host enabling the controller.<br>Some models require a different time (seeSection 13 Device Profiles) <br>If a PCIe Conventional Reset occurs while a device is shutdown (i.e., the CSTS.SHST field is<br>set to 10b), then this requirement may cause the device to transition to a state where a<br>power loss would be unexpected. This requirement overrides the requirement in the NVM<br>Express Base specification for the controller to be ready to be powered off until CC.EN<br>transitions from 0b to 1b following a controller shutdown.|
|TTR-23|The device shall not support NVM Subsystem Shutdown.|

**7.2.2 Incomplete/Unsuccessful Shutdown**

An incomplete/unsuccessful shutdown is a Normal or Abrupt power down that did not complete 100% of
the shutdown sequence for any reason that causes the device to be unable to guarantee data/metadata
integrity (e.g., firmware hang/crash, capacitor failure, PLP circuit failure, etc.).

<!-- page 154 -->
|Requirement<br>ID|Description|
|---|---|
|INCS-1|When the power-loss protection mechanism fails for any reason while power is applied, the<br>device shall set Critical Warning bit 4 to 1b in the SMART / Health Information log page (Log<br>Identifier 02h) and transition to the write behavior as defined in the EOL/PLP Failure Mode<br>(Feature Identifier C2h).|
|INCS-2|The device shall incorporate a shutdown checksum or flag as the very last piece of data<br>written to flash to detect incomplete shutdown.|
|INCS-3|The checksum or flag in INCS-2 shall be used on power-up to confirm that the previous<br>shutdown was 100% successful.|
|INCS-4|An incomplete/unsuccessful shutdownthat causes the device to be unable to guarantee<br>data/metadata integrity shall result in an increase in the Incomplete Shutdowns field<br>(SMART-15) in the SMART / Health Information Extended log page (Log Identifier C0h). on<br>the subsequent power up, the device shall set bit 3 of the Critical Warning field in the<br>SMART / Health Information (Log Identifier 02h) to 1b.|
|INCS-5|If the device is in read-only mode (i.e., bit 3 in the Critical Warning field is set to 1b in the<br>SMART / Health Information log page) for any reason, then the device shall still support<br>NVMe Admin commands, including commands that result in a purge (seeSEC-43).|
|INCS-6|<br>If the Error Recovery (Log Identifier C1h) is supported, when the device increments the<br>Incomplete Shutdowns field in SMART / Health Information Extended log page (Log<br>Identifier C0h), it shall use the following recovery procedure at the next power up:<br> <br>|

<!-- page 155 -->
|Requirement<br>ID|Description|
|---|---|
|INCS-7|If the Error Recovery (Log Identifier C1h) is not supported, when the device increments the<br>Incomplete Shutdowns field in SMART / Health Information Extended log page (Log<br>Identifier C0h), it shall use the following recovery procedure at the next power up:|

### **7.3 End to End Internal Data Protection**

|Requirement ID|Description|
|---|---|
|E2E-1|All user data and metadata shall be protected using overlapping protection mechanisms<br>throughout the entire read and write path in the device including all storage elements<br>(registers, caches, SRAM, DRAM, NAND, etc.).|
|E2E-2|At least one bit of correction and 2 bits of detection is required for all memories. This shall<br>be for all memories regardless of function.|
|E2E-3|The entire DRAM addressable space shall be protected with at least one-bit correction and<br>2 bits of detection scheme (SECDED). This includes but is not limited to the following:<br>• <br>Flash translation layer (FTL).<br>• <br>Mapping tables (including metadata related to deallocated LBAs).<br>• <br>Journal entries.<br>• <br>Firmware scratch pad.<br>• <br>System variables.<br>• <br>Firmware code.|
|E2E-4|Silent data corruption shall not be tolerated under any circumstances.|
|E2E-5|The device shall include a mechanism to protect against returning the data from the wrong<br>logical block address (LBA), including previous copies from the same LBA, to the host. It is<br>acceptable if the device stores additional/modified information to provide protection<br>against returning wrong data to the host. Device shall perform host LBA integrity checking<br>on all transfers to and from the media.|
|E2E-6|All device metadata, firmware, firmware variables, and other device system data shall be<br>protected by at least a single bit detection scheme.|

<!-- page 156 -->
|Requirement ID|Description|
|---|---|
|E2E-7|Any memory buffers that are utilized to accelerate data transfer (read-ahead buffers for<br>example) shall follow the protection scheme outlined in E2E-5.|

### **7.4 Behavior on Firmware Crash, Panic or Assert**

|Requirement ID|Description|
|---|---|
|CRASH-1|While the device is in a failed state in which it can no longer accept Write commands (e.g.,<br>firmware crash, panic, or assert), the device shall allow read access only if it can guarantee<br>data integrity.|
|CRASH-2|While the device is in a failed state, that is not a controller failure (e.g., firmware crash,<br>panic, or assert), the device shall still support NVMe Admin commands including the ability<br>to read any failure logs from the device to determine the nature of the failure.<br> <br>After a controller failure, the device may fail Admin commands sent by the host prior to<br>completion of the Panic Reset Action in the Error Recovery workflow (seeEREC-2).|
|CRASH-3|<br>Upon device completion of the actions specified in Panic Reset Action (seeEREC-2) and<br>Device Recovery Action (seeEREC-3), if the device is successfully recovered from a failed<br>state, then the device shall function normally as specified in this specification including<br>read and write access at full performance.|
|CRASH-4|Obsolete|
|CRASH-5|The device shall have a mechanism (e.g., watchdog timer) to allow recovery from hangs of<br>the firmware.  The timeout interval of this mechanism shall be less than 2 seconds.|

### **7.5 Annual Failure Rate (AFR)**

|Requirement ID|Description|
|---|---|
|REL-1|The device shall meet an MTBF of 2.5 million hours (AFR of <= 0.35% per JEDEC JESD 218) <br>under the following environmental conditions:<br>**Specification**<br>**Environment**<br>**Requirement**<br>**Temperature** <br>Operational<br>● 0˚C to 50˚C (32˚F to 122˚F)<br>● < 20°C (68˚F) per hour gradient<br>Non-Operational<br>● -40˚C to 70˚C (-40˚F to 158˚F)<br>● < 30˚C (86˚F) per hour gradient<br>**Humidity** <br>Operational<br>● 10% to 90% non-condensing<br>● Yearly weighted average: < 80% RH<br>`o` 90% of year: < 80%<br>`o` 10% of year: 80% to 90%<br>● Maximum dewpoint: 29.4°C (85°F)<br>Non-Operational<br>● 5% to 95% non-condensing<br>● 38°C (100.4°F) maximum wet bulb temperature|

|Specification|Environment|Requirement|
|---|---|---|
|**Temperature**|Operational|● 0˚C to 50˚C (32˚F to 122˚F)<br>● < 20°C (68˚F) per hour gradient|
|**Temperature**|Non-Operational|● -40˚C to 70˚C (-40˚F to 158˚F)<br>● < 30˚C (86˚F) per hour gradient|
|**Humidity**|Operational|● 10% to 90% non-condensing<br>● Yearly weighted average: < 80% RH<br>`o` 90% of year: < 80%<br>`o` 10% of year: 80% to 90%<br>● Maximum dewpoint: 29.4°C (85°F)|
|**Humidity**|Non-Operational|● 5% to 95% non-condensing<br>● 38°C (100.4°F) maximum wet bulb temperature|

<!-- page 157 -->
|Specification|Environment|Requirement|
|---|---|---|
|**Temperature**|Operational|● 0˚C to 55˚C (32˚F to 131˚F)<br>● < 20°C (68˚F) per hour gradient|
|**Temperature**|Non-operational|● -40˚C to 70˚C (-40˚F to 158˚F)<br>● < 30˚C (86˚F) per hour gradient|
|**Humidity**|Operational|● 10% to 90% non-condensing<br>● Maximum dewpoint: 29.4°C (85°F)|
|**Humidity**|Non-operational|● 5% to 95% non-condensing<br>● 38°C (100.4°F) maximum wet bulb temperature|

|Requirement ID|Description|
|---|---|
|REL-2|The device shall meet an MTBF of 2.0 million hours (AFR of <= 0.44% per JEDEC JESD 218) <br>under the following environmental conditions:<br>**Specification**<br>**Environment**<br>**Requirement**<br>**Temperature** <br>Operational<br>● 0˚C to 55˚C (32˚F to 131˚F)<br>● < 20°C (68˚F) per hour gradient<br>Non-operational<br>● -40˚C to 70˚C (-40˚F to 158˚F)<br>● < 30˚C (86˚F) per hour gradient<br>**Humidity** <br>Operational<br>● 10% to 90% non-condensing<br>● Maximum dewpoint: 29.4°C (85°F)<br>Non-operational<br>● 5% to 95% non-condensing<br>● 38°C (100.4°F) maximum wet bulb temperature|
|REL-3|Supplier shall provide the temperature conditions used to determine the MTBF.|
|REL-4|Supplier shall provide AFR de-rating curves for the Temperature range shown in<br>requirement REL-2 for up to 70˚C (158˚F).|
|REL-5|The AFR targets in REL-1 (MTBF of 2.5 million hours) and REL-2 (MTBF of 2.0 million hours)<br>shall be maintained up to a continuous reported composite temperature of 77˚C (170 °F)<br>(WCTEMP) with less than 1% of the device power on time above WCTEMP.|
|REL-6|The device shall have no exposed raw copper on any component.  All copper surfaces,<br>pads, fingers, etc. on all components shall be covered with a minimally reactive coating<br>(e.g., resin packaging material on ICs, gold plating on PCB connectors/pads, silver-tin<br>coatings on component leads and IC balls).|

### **7.6 Background Data Refresh**

|Requirement ID|Description|
|---|---|
|BKGND-1|The device shall support background data refresh while the device is powered on to ensure<br>there is no data-loss due to power-on retention issues.|
|BKGND-2|The device shall be designed and tested to support the normal NAND operating<br>temperature.|
|BKGND-3|Background data refresh shall cover the entire device and be designed to continuously run<br>in the background and not just during idle periods.|

### **7.7 Wear-leveling**

|Requirement ID|Description|
|---|---|
|WRL-1|The device shall utilize the entire Endurance Group media capacity range whenever the<br>device needs to wear-level a block.  The device shall not restrict the wear-leveling range to<br>a subset of the Endurance Group media capacity unless otherwise specified.  If the device<br>does not support Endurance Groups, it shall wear-level across the entire physical media.|

### **7.8 Power Loss Protection**

|Requirement ID|Description|
|---|---|
|PLP-1|The device shall support full power-loss protection for all acknowledged data and<br>metadata.|

<!-- page 158 -->
|Requirement ID|Description|
|---|---|
|PLP-2|The Power-loss protection health check shall not impact I/O latency and performance.|
|PLP-3|Power-loss protection health check shall be performed by the device at power-on (prior to<br>accepting any writes) and at least once every time interval as specified inSPLPI-13.|
|PLP-4|<br>While performing the power-loss protection health check, the device shall still have<br>enough energy to be able to handle an abrupt power loss properly.|
|PLP-5|The firmware/hardware algorithm shall deploy safeguards to prevent false detection of<br>power loss protection failure. Example of a false detection would be a glitch in any of the<br>power loss circuitry readings which would cause a transient event to trigger a false power<br>loss protection failure when the power loss protection hardware is healthy.|
|PLP-6|The device shall implement a power-loss protection (PLP) health check which can detect<br>the capacitor holdup energy margin reported in the Capacitor Health field specified in<br>SMART-19 in SMART / Heath Information Extended log page (Log Identifier C0h). The PLP<br>health check shall not just check for open/short capacitor conditions but shall measure the<br>true available margin energy.|
|PLP-7|The factory default PLP Health Check Interval shall be 15 minutes (seeGPLPI-2).|
|<br>PLP-8|<br>The default PLP Health Check Interval of 15 minutes (seeGPLPI-2) shall not cause the<br>device to violateREL-1 orREL-2.|

<!-- page 159 -->
|Requirement ID|Description|
|---|---|
|PLP-9|The device shall use the following workflow for the PLP Health Check (seeINCS-1) for PLP<br>AEN details):<br>Power On<br>PLP<br>Circuitry<br>Self-test<br>PLP Circuitry<br>Good?<br>Continue Normal<br>Operation<br>Send PLP Loss AEN<br>Continue<br>Operation per<br>SROWTM-13<br>No<br>(Based on PLP-5)<br>Yes<br>Flush Any Volatile<br>Metadata to Non-<br>volatile Memory<br>Flush Any Volatile<br>User Data to Non-<br>volatile Memory<br>PLP Test<br>Interval Timer<br>Expired<br>Yes<br>No<br>Begin Operating<br>per EOL/PLP<br>Failure Mode Set<br>Feature Identifier<br>(0xC2)<br>SROWTM-13<br> = 11b<br>No<br>Yes|

<!-- page 160 -->
### **7.9 Device Limits**

|Requirement ID|Description|
|---|---|
|DEVLMT-1|The device shall not have any architectural restrictions, other than P/E cycle restrictions of<br>the NAND, on the number of times any of the following events can occur:<br>• <br>Firmware downloads and activation supported (seeFWUP-2); or<br>• <br>Changing password when taking/changing ownership via TCG; or<br>• <br>Commands that result in a purge (seeSEC-43); or<br>• <br>Power cycles; or<br>• <br>Set Features command/Get Features command (including power state changes); or<br>• <br>Log page or debug log retrievals.<br>This is not meant to be a test until fail requirement.|

## **8 Endurance**

### **8.1 Endurance Data**

|Requirement ID|Description|
|---|---|
|ENDUD-1|The device documentation shall include the number of physical bytes able to be written to<br>the device assuming a write amplification of 1.  The units should be gigabytes (10^9 bytes).|
|ENDUD-2|The preconditioning steps to test device performance at end-of-life are:<br>• <br>50/50 Read/Write workload (by number of I/Os).<br>• <br>4kiB Read accesses aligned to 4kiB boundaries.<br>• <br>128kiB Write accesses aligned to 128kiB boundaries.<br>• <br>Random pattern of Read addresses.<br>• <br>Sequential pattern of Write addresses.<br>• <br>100% active range.<br>• <br>80% full device (80% data, 20% free space).<br>• <br>0% compressible data.<br>• <br>Ambient temperature 35°C (95°F).<br>• <br>Short-stroked device if capacity is 2 TB or greater (seeEOL-2).|
|ENDUD-3|The Percentage Used in the SMART / Heath Information log page (Log Identifier 02h) shall<br>track linearly with bytes written and at 100% it shall match the EOL value specified in<br>ENDUD-1.|

### **8.2 Retention Conditions**

Since there are several factors that impact the device endurance, the following table provides the
requirements for the datacenter environment:

|Requirement ID|Description|
|---|---|
|RETC-1|Non-Operational (Powered-off) device data retention time (end of life) shall be at least 1<br>month at 40°C (104°F). SeeSection 13 Device Profiles for specific retention requirements.<br>Specific Devices Profiles may have longer data retention time requirements.|

<!-- page 161 -->
|Requirement ID|Description|
|---|---|
|RETC-2|Operating (Powered-on) data retention shall be at least 7 years. For purposes of this<br>requirement, the assumption is that the Terabytes Written (TBW) capability of the devices<br>is used linearly over the lifetime. This requirement does not imply any specific warranty<br>period.|
|RETC-3|The device shall not throttle its performance based on the endurance metric (endurance<br>throttling).|

### **8.3 Shelf Life**

|Requirement ID|Description|
|---|---|
|SLIFE-1|A new device may be kept as a datacenter spare and therefore shall be fully functional<br>even if it sits on the shelf for at least 5 years at 25°C (77°F) before getting installed in the<br>server. The device shall be new in box factory state.|
|SLIFE-2|Shelf-life shall be documented and provided to the customer.|

### **8.4 End-of-Life (EOL)**

|Requirement ID|Description|
|---|---|
|EOL-1|Several types of samples are required for EOL testing:<br>a. Beginning of Life (Short stroked if required by EOL-2).<br>b. End of Life (Short stroked if required by EOL-2).<br>c. End of Life (Not short stroked if different than item b).<br>EOL is defined as the Total Bytes Written (TBW) specification has been surpassed (see<br>ENDUD-1) or the non-volatile media endurance limit (e.g., NAND cycling limit causes the<br>block to be unwritable) has been reached; whichever is earliest.|
|EOL-2|On 2 TB or larger devices, there shall be a method to “short stroke” the device. Media<br>reserved for background operations shall be proportionally adjusted. Short Stroke<br>firmware capacity shall be reduced to a range of 10% to 3% of full capacity. Short stroke<br>shall cover all the channels/dies/planes while maintaining the native performance of the<br>device.|
|EOL-3|Obsolete.|
|EOL-4|The device shall continue to operate in a read/write mode until the conditions in EOL-5 are<br>reached or until another type of error causes the device to be unable to continue to<br>operate in read/write mode (e.g., the device enter read-only mode due to the conditions<br>inINCS-4).|

<!-- page 162 -->
|Requirement ID|Description|
|---|---|
|EOL-5|The device shall switch to Read Only Mode (ROM) when the Available Spare field in the<br>SMART / Health Information log page (Log Identifier 02h) reaches 0%.  A value of 0%<br>represents the device state where there is an insufficient number of spare blocks to<br>support Host writes.  The Available Spare field shall report a value of 0% before the device<br>exhausts all available spare blocks so that there are still sufficient available spare blocks<br>remaining to handle blocks going bad during read operations.<br>When the device switches to ROM due to this condition, bit 2 and bit 3 of the Critical<br>Warning field in the SMART / Health Information log page shall be set to 1b.<br>If the value reported in the Available Spares field falls below the value reported in the<br>Available Spare Threshold field, then the device shall set bit 0 of the Critical Warning field<br>in the SMART / Health Information log page to 1b and generate a SMART / Health Status<br>event if that event is enabled and an Asynchronous Event Request command is<br>outstanding.|
|EOL-6|The device shall have enough spare blocks so that the Percentage Used field value in the<br>SMART / Health Information log page reaches 100% prior to the Available Spare field value<br>falling below the Available Spare Threshold field value.  See ENDUD-1 andENDUD-3 for<br>related Percentage Used field value requirements.|
|EOL-7|The update granularity for the Percentage Used field and Available Spare field in the<br>SMART / Health Information log page shall be 1%.|
|EOL-8|The Available Spare Threshold shall be set such that the Available Spare does not reach 0%<br>for at least three days after crossing the Available Spare Threshold assuming a worst-case<br>write workload.|

## **9 Thermal**

### **9.1 Data Center Altitude**

|Requirement ID|Description|
|---|---|
|THERM-1|Support for devices in data centers located at an altitude of up to 10,000 feet above sea<br>level is required (e.g., thermals, cosmic rays, etc.). When considering thermals, there shall<br>be no de-rating up to 6,000 feet above sea level. Above 6,000 feet the derating shall be<br>0.9°C (1.6°F)/1000ft.|
|THERM-2|A thermal study with each platform is required and shall be provided to the customer. The<br>thermal design shall be validated up to 35°C (95°F) ambient temperature for the platform<br>with a worst-case airflow of 1.5 meters per second at sea level.|
|THERM-3|The device shall operate normally with relative humidity to be between 10% and 90%.|

<!-- page 163 -->
### **9.2 Thermal Throttling**

|Requirement ID|Description|
|---|---|
|TTHROTTLE-1|The device shall implement a thermal throttling mechanism to protect the device in case<br>of a failure or an excursion that causes the device’s temperature to increase above its<br>maximum specified temperature. This mechanism shall check device temperature at a<br>frequency sufficient to ensure that the thermal throttling mechanism protects the device.<br>This temperature check frequency shall be at least once per second.|
|TTHROTTLE-2|When the device begins throttling performance due to an over temperature condition, an<br>Asynchronous Event Request shall be completed with the Asynchronous Event Type field<br>set to 001b (SMART / Health status) and the Asynchronous Event Information field set to<br>01h (Temperature Threshold), if that event is enabled and an Asynchronous Event Request<br>command is outstanding. The device shall set bit 1 of the SMART / Health Information log<br>page (Log Identifier 02h) Critical Warning field to 1b.|
|TTHROTTLE-3|Thermal throttling shall only be engaged under conditions that are able to cause significant<br>reduction in device service life, such as excessive server ambient temperature. The<br>required behavior is illustrated in the following figure:|
|TTHROTTLE-4|The firmware algorithm shall deploy safeguards to prevent a false activation of either<br>thermal throttling or thermal shutdown. An example of a false activation would be a glitch<br>in any of the sensor readings which would cause the composite temperature to reach the<br>thermal throttling or thermal shutdown limit.|
|TTHROTTLE-5|A composite temperature of 77°C (170.6°F) shall be used to start throttling. Single stage<br>and multi-stage throttling are both allowed.|
|TTHROTTLE-6|Thermal throttling shall not start based on the rate of temperature increase or slew rate.|
|TTHROTTLE-7|When the device is in the thermal throttling state and the temperature drops back down<br>below 75°C (167°F), the device shall exit the thermal throttling state and an Asynchronous<br>Event Request shall be completed with the Asynchronous Event Type field set to 001b<br>(SMART / Health status) and the Asynchronous Event Information field set to 01h<br>(Temperature Threshold), if that event is enabled and an Asynchronous Event Request<br>command is outstanding. The device shall clear bit 1 of the SMART / Health Information<br>log page (Log Identifier 02h) Critical Warning field to 0b.|

<!-- page 164 -->
|Requirement ID|Description|
|---|---|
|TTHROTTLE-8|When the device reaches a critical temperature on any component it shall report a<br>composite temperature of 85°C (185°F) and an Asynchronous Event Request shall be<br>completed with the Asynchronous Event Type field set to 001b (SMART / Health status)<br>and the Asynchronous Event Information field set to 01h (Temperature Threshold), if that<br>event is enabled and an Asynchronous Event Request command is outstanding, before the<br>device shuts off to protect itself.|
|TTHROTTLE-9|The device shall report a value of 015Eh (77°C) in the Warning Composite Temperature<br>Threshold (WCTEMP) field of the Identify Controller Data structure.|
|TTHROTTLE-10|The device shall report a value of 0166h (85°C) in the Critical Composite Temperature<br>Threshold (CCTEMP) field of the Identify Controller Data structure.|
|TTHROTTLE-11|If the Composite Temperature is greater than or equal to 77°C (170.6°F), the device shall<br>update the Warning Composite Temperature Time field of the SMART / Health Information<br>log page (Log Identifier 02h) once per minute until one of the following occurs:<br>• <br>The device Composite Temperature falls below 75°C (167°F); or<br>• <br>The device shuts down due to an over Critical Temperature condition; or<br>• <br>The device is power cycled.|
|TTHROTTLE-12|The temperature limits of internal components within the device shall govern the thermal<br>throttling algorithms.  In addition, the thermal throttling algorithms shall prevent excessive<br>case temperature (see TTHROTTLE-14).|
|TTHROTTLE-13|In all throttling states including the lowest throttle state, the device shall not enter a read-<br>only mode and shall continue to attempt to process all commands, including commands<br>that write media, unless the device shuts down, e.g., due to a Critical Temperature<br>condition.|
|TTHROTTLE-14|The critical device case (i.e., touch) temperature shall be the TS2 limits as specified in IEC<br>62368-1 3rd Edition or later.  For non-case devices the hottest surface shall be used for the<br>device touch temperature.<br>The TS2 100oC limit is prohibited for some form factors (seeFFM2-15, FFE1S-13, and<br>FFE1L-13).|

### **9.3 Temperature Reporting**

|Requirement ID|Description|
|---|---|
|TRPT-1|The device shall expose the current raw sensor readings from all the sensors on the device.|
|TRPT-2|A device shall report a composite temperature that has an accuracy better than or equal to<br>+/-1°C (1.8°F) degrees. As a consequence, two devices of the same model shall not report<br>a composite temperature greater than 2°C (3.6°F) apart under the same environmental<br>conditions, slot location, and workload.|
|TRPT-3|A device shall use temperature sensors that have an accuracy better than or equal to +/-<br>1°C (1.8°F) degrees.|
|TRPT-4|The supplier shall provide to the customer the equation, settings, and thresholds used to<br>calculate the composite temperature.|
|TRPT-5|When calculating the composite temperature, the device shall take into account the<br>temperature of all of the major thermal components (SOC, DRAM, NAND, PMIC, etc.).|

<!-- page 165 -->
|Requirement ID|Description|
|---|---|
|TRPT-6|The reported composite temperature shall be the same for all controllers in the NVM<br>subsystem.|

### **9.4 Thermal Shutdown**

|Requirement ID|Description|
|---|---|
|THRMS-1|The device shall shut down to protect itself against data loss or damage due to extreme<br>temperatures. The shutdown temperature value shall be at a composite temperature of<br>85°C (185°F). Shutdown shall preserve all user data.|
|THRMS-2|The device shall not process NVM I/O commands while in thermal shutdown. If it is safe to<br>do so, the device shall process Admin commands (in-band and out-of-band), NVMe-MI <br>Command Set commands, and PCIe Command Set commands while in thermal shutdown.|
|THRMS-3|The device shall only come out of thermal shutdown as a result of a main power cycle.|

## **10 Form Factor Requirements**

### **10.1 Generic Form Factor Requirements**

|Requirement ID|Description|
|---|---|
|GFF-1|The device shall be compliant to PCI Express Base Specification, Revision 4.0, Version 1.0<br>(or later).|
|GFF-2|The vendor shall provide a PCIe compliance report that demonstrates compliance.|
|GFF-3|The device shall support lane reversal with all lanes connected or partially connected lanes<br>on both the lower-numbered lanes and higher-numbered lanes of the device (e.g., a x4<br>device shall support lane reversal for x4, x2, and x1 connections on both the lower-<br>numbered lanes and higher-numbered lanes of the device).|
|GFF-4|The device shall train to x1 when the upstream device provides only one lane, to x2 when<br>2 lanes are provided and to x4 when 4 lanes are provided. This requirement applies to<br>both the lower-numbered lanes and higher-numbered lanes of the device.|
|GFF-5|The device shall support hot swap on form factors that support hot swap.|
|GFF-6|A CAD file of each supported form factor shall be provided to the customer.|

### **10.2 Power Consumption Measurement Methodology**

|Requirement ID|Description|
|---|---|
|PCM-1|The device Max Average Power (MAP) consumption for any workload shall not exceed the<br>Maximum Power (MP) of the current NVMe Power State measured over a 1 second<br>window with a sampling rate of 2 ms or less. The measurement duration shall be at least<br>15 minutes on a pre-conditioned device. This requirement defines the measurement<br>methodology for Maximum Sustained Device Power as defined in SFF-TA-1009 revision<br>3.0.|
|PCM-2|The device peak power for any workload shall be measured over a 100 uS window with a<br>sampling interval of 4 uS or less. The measurement duration shall be at least 15 minutes<br>on a pre-conditioned device.|

<!-- page 166 -->
|Requirement ID|Description|
|---|---|
|PCM-3|For devices whose max average power consumption is less than or equal to 25 W, the peak<br>power shall be no more than 1.5x the max average power.  For devices whose max average<br>power consumption is greater than 25 W but less than or equal to 29W the peak power<br>shall be no more than 37.5 W.  For devices whose max average power consumption is<br>greater than 29 W, the peak power shall be no more than 1.3x the max average power.<br>The max average power is defined in PCM-1.|
|PCM-4|The Maximum Power field in each Power State Descriptor data structure in the Identify<br>Controller data structure shall indicate the maximum average power measured as<br>specified by PCM-1.|

### **10.3 Power Levels**

|Requirement ID|Description|
|---|---|
|PWR-1|The Power Management (Feature Identifier 02h) shall be supported and the NVMe Power<br>State Descriptor table in Identify Controller Data Structure bytes 3071:2048 shall be filled<br>out per the NVM Express Base Specification.|
|PWR-2|Obsolete.  SeeDCLP-9 andSection 4.8.11.1 DSSD Power State Descriptor.|
|<br>PWR-3|<br>The method of measurement for Maximum Average Power (MAP) is defined inPCM-1. <br>MAP values are reported in the Maximum Power (MP) field of NVMe Power State<br>Descriptors.|
|PWR-4|Power state entries above the maximum rated power envelope of the device shall not be<br>populated in the NVMe Power State Descriptor table in Identify Controller Data Structure<br>bytes 3071:2048.|
|PWR-5|The Set Features for Power Management (Feature Identifier 02h) with the SV bit 31 in<br>Command Dword 10 shall be supported so that the power level can be set and will be<br>saved across power cycles.|
|PWR-6|The device, regardless of form factor or capacity, shall have an idle power of 5 W or less<br>per European Lot 9 regulation.Devices shall automatically reduce power consumption to<br>5 W or less when idle without impacting latency or performance.|
|PWR-7|The device shall not consume more power than the PCI-SIG Slot Capabilities register Slot<br>Power Limit regardless of other settings (e.g., DSSD Power State, NVMe Power State).|
|PWR-8|The device shall not use the same Maximum Power (MP) value in more than one<br>supported NVMe Power State Descriptor unless otherwise specified.|
|PWR-9|The device shall not support Non-Operational Power State Permissive Mode (i.e., bit 1 of<br>the Controller Attributes field in the Identify Controller data structure shall be cleared to<br>0b).|

### **10.4 M.2 Form Factor Requirements**

|Requirement ID|Description|
|---|---|
|FFM2-1|The device shall adhere to the M.2 specification with a size of 22 mm x 110 mm or 22 mm<br>x 80 mm.|
|FFM2-2|The bottom-side height shall not exceed 1.5 mm.|
|FFM2-3|The top-side height shall not exceed 3.2 mm. Some models may need to be thinner (see<br>Section 13 Device Profiles).|

<!-- page 167 -->
|Requirement ID|Description|
|---|---|
|FFM2-4|The device shall use an M key.|
|FFM2-5|The device shall support a minimum of PCIe Gen4 x4.|
|FFM2-6|The device shall support driving an activity LED through the connector via LED_1#.|
|FFM2-7|The LED should be lit solidly when power is applied and flashing when there is traffic going<br>to the SSD.|
|FFM2-8|The device shall not use any pins that are defined in the M.2 specification for vendor<br>unique functionality.|
|FFM2-9|The device shall support a protection scheme that protects against NAND block level<br>failures.|
|FFM2-10|The protection scheme must also support NAND plane level failures without data or<br>metadata loss.|
|FFM2-11|The Label shall be placed on the top side of the device.|
|FFM2-12|The device’s SMBus electricals shall comply with version 3.2 (see<br>_http://www.smbus.org/specs/SMBus_3_2_20220112.pdf_) and in PCI Express M.2 Revision<br>4.2 or later.|
|FFM2-13|The device’s SMBus protocol shall comply with version 3.2 (see<br>_http://www.smbus.org/specs/SMBus_3_2_20220112.pdf_).|
|FFM2-14|<br>The default max average power for M.2 devices shall not exceed 8.25 W and the peak<br>power shall comply toPCM-3.|
|FFM2-15|<br>The case (i.e., touch) temperature shall not exceed 80oC. The 100oC TS2 limit does not<br>apply (seeTTHROTTLE-14).|

### **10.5 E1.S Form Factor Requirements**

|Requirement ID|Description|
|---|---|
|FFE1S-1|The device shall adhere to the latest revision of SFF-TA-1006.|
|FFE1S-2|At a minimum, the device shall support PCIe Gen4 x4.|
|FFE1S-3|The device shall support activity and error LEDs.|
|FFE1S-4|The activity LED shall be lit solidly when power is applied and flashing when there is traffic<br>going to the device.|
|FFE1S-5|The device shall support a protection scheme that protects against NAND block level<br>failures.|
|FFE1S-6|The protection scheme must also support NAND plane level failures without data or<br>metadata loss.|
|FFE1S-7|The amber LED shall meet the requirements specified in SFF-TA-1009. The functioning of<br>the Amber LED shall be independent of the 12 V, 3.3 Vaux and the state of the PWRDIS pin.|
|FFE1S-8|The thermal performance of the 9.5 mm, 15 mm, and 25 mm cases and their associated<br>pressure drops shall be provided.|
|FFE1S-9|The PWRDIS pin shall be supported.|
|FFE1S-10|The SMBus electrical connections shall follow the “DC Specification For 3.3 V Logic<br>Signaling” as defined in SFF-TA-1009 revision 2.0. Including Vih1 with a max of 3.465 V.|
|FFE1S-11|The device’s SMBus protocol shall comply to version 3.2 (see<br>_http://www.smbus.org/specs/SMBus_3_2_20220112.pdf_).|
|FFE1S-12|<br>A x4 device shall only have a 1C connector.|

<!-- page 168 -->
|Requirement ID|Description|
|---|---|
|FFE1S-13|The case (touch) temperature shall not exceed 80oC. The 100oC TS2 limit does not apply<br>(seeTTHROTTLE-14).|
|FFE1S-14|<br>The device shall support the amber LED and the green LED.  The device shall not support<br>any other LED colors.|

### **10.6 E1.L Form Factor Requirements**

|Requirement ID|Description|
|---|---|
|FFE1L-1|The device shall adhere to the latest revision of SFF-TA-1007.|
|FFE1L-2|At a minimum, the device shall support PCIe Gen4 x4.|
|FFE1L-3|The device shall support activity and error LEDs.|
|FFE1L-4|The activity LED shall be lit solidly when power is applied and flashing when there is traffic<br>going to the device.|
|FFE1L-5|The device shall support a protection scheme that protects against NAND block level<br>failures.|
|FFE1L-6|The protection scheme must also support NAND plane level failures without data or<br>metadata loss.|
|FFE1L-7|The amber LED shall meet the requirements specified in SFF-TA-1009. The functioning of<br>the Amber LED shall be independent of the 12 V, 3.3 Vaux and the state of the PWRDIS pin.|
|FFE1L-8|The thermal performance of the 9.5 mm and 18 mm cases and their associated pressure<br>drops shall be provided.|
|FFE1L-9|The PWRDIS pin shall be supported.|
|FFE1L-10|The SMBus electrical connections shall follow the “DC Specification For 3.3 V Logic<br>Signaling” as defined in SFF-TA-1009 revision 2.0. Including Vih1 with a max of 3.465 V.|
|FFE1L-11|The device’s SMBus protocol shall comply to version 3.2 (see<br>_http://www.smbus.org/specs/SMBus_3_2_20220112.pdf_).|
|FFE1L-12|<br>A x4 device shall only have a 1C connector.|
|FFE1L-13|The case (touch) temperature shall not exceed 80oC. The 100oC TS2 limit does not apply<br>(seeTTHROTTLE-14).|
|FFE1L-14|<br>The device shall support the amber LED and the green LED.  The device shall not support<br>any other LED colors.|

### **10.7 E3 Form Factor Requirements**

|Requirement ID|Description|
|---|---|
|FFE3-1|The device shall adhere to the latest revision of SFF-TA-1008.|
|FFE3-2|The device shall adhere to the latest revision of SFF-TA-1009.|
|FFE3-3|The device shall support Separate Reference Clocks with Independent SSC (SRIS)<br>requirements of the PCI Express Base Specification.<br>Devices shall support SRIS detection and switching as described in SFF-TA-1009 and<br>support the full jitter specified by the PCI Express Base Specification (see FFE3-4).<br>The device shall support switching between SRIS and common clock on a power cycle and<br>on assertion/de-assertion of PERST# with or without a power cycle as described in<br>SFF-TA-1009 and shall not switch clocking modes under any other conditions.|

<!-- page 169 -->
|Requirement ID|Description|
|---|---|
|FFE3-4|The device shall be compliant to PCI Express Base Specification, Revision 5.0, Version 1.0<br>(or later).|

### **10.8 SFF-8639 (U.2/U.3) Form Factor Requirements**

|Requirement ID|Description|
|---|---|
|FF8639-1|The device shall adhere to SFF-TA-1001 revision 1.1 or later and the PCI Express SFF-8639<br>Module Specification, Revision 4.0, Version 1.0.  Compliance to any later Revision of the<br>PCI Express SFF-8639 Module Specification is prohibited.|
|FF8639-2|The device shall support Separate Reference Clocks with Independent SSC (SRIS)<br>requirements of the PCI Express Base Specification.<br>Devices shall support SRIS detection and switching as described in the PCI Express SFF-<br>8639 Module Specification (see FF8639-1) and support the full jitter specified by the PCI<br>Express Base Specification Revision 4.0.<br> <br>The device shall support switching between SRIS and common clock on a power cycle and<br>on assertion/de-assertion of PERST# with or without a power cycle and shall not switch<br>clocking modes under any other conditions.|
|FF8639-3|All 2.5” SFF NVMe devices shall support the activity LED function on Pin 11 of the SFF-8639<br>connector.<br>Pin 11 shall assert/de-assert (see FF8639-4) while processing one or more commands.<br>Once asserted due to command processing, pin 11 shall remain asserted for 50 ms and<br>then shall be de-asserted for 50 ms.  This assert/de-assert behavior shall continue while<br>command processing continues (i.e., the LED is usually off, but flashes on and off while<br>commands are processed).<br>Once pin 11 is de-asserted for 50 ms, it shall remain de-asserted as long as there is no<br>command processing activity.|
|FF8639-4|Active State (pin asserted and LED on) is defined as logic “0” (i.e., < 0.3 V) on Pin 11.<br>Inactive State is defined as logic “1” (i.e., > 3.3 V) on Pin 11.<br>A device’s internally initiated background activity or maintenance routine that is not<br>commanded to be performed from the host shall not cause the LED to be in the Active<br>State (logic “0” level).|

## **11 Management Support**

### **11.1 NVMe Basic Management Command (Appendix A) Requirements**

|Requirement ID|Description|
|---|---|
|SMBUS-1|The device shall support the NVMe Basic Management Command as defined in Appendix A<br>of the NVM Express Management Interface Specification, Revision 1.2d:<br>(https://nvmexpress.org/wp-content/uploads/NVM-Express-Management-Interface-<br>Specification-1.2d-2024.01.10-Ratified.pdf).|

<!-- page 170 -->
|Bit|Description|
|---|---|
|7|Shall be set to 1b.  SeeCommand Code 242 for the definition of Secure Boot<br>Failure Reporting.|
|6|Shall be set to 1b.  SeeCommand Code 242 for the definition of Secure Boot<br>Failure Reporting.|
|5|Shall be set to 1b and a valid Recovery code shall be entered in byte 244.  These<br>codes are defined in the_Platform Root-of-Trust for Recovery_.  Use of these codes is<br>explained in the_OCP Hardware Secure Boot White Paper_.|
|4:0|<br> Reserved.  Shall be cleared to zero.|

|Requirement ID|Description|
|---|---|
|SMBUS-2|SMBus Block Read protocol and Byte Read protocol shall be supported. As an override of<br>the NVM Express Management Interface Specification, SMBus Block Write protocol and<br>Byte Write protocol shall also be supported.|
|SMBUS-3|The device shall implement the SMBus format as show inSection 11.2 - NVMe Basic<br>Management Command (Appendix A) Data Format.|
|SMBUS-4|<br>Unless otherwise noted, the default value for the Firmware Update Flags field (byte 91) in<br>the SMBus Data structure shall be set to FFh.|
|SMBUS-5|The Secure Boot Failure Feature Reporting Supported bit at offset 243 shall be supported<br>and set to 1b.|
|SMBUS-6|When there is a secure boot failure the device shall report the failure with the following<br>behavior:<br>**Bit**<br>**Description**<br>7 <br>Shall be set to 1b. SeeCommand Code 242 for the definition of Secure Boot<br>Failure Reporting.<br>6 <br>Shall be set to 1b. SeeCommand Code 242 for the definition of Secure Boot<br>Failure Reporting.<br>5 <br>Shall be set to 1b and a valid Recovery code shall be entered in byte 244. These<br>codes are defined in the_Platform Root-of-Trust for Recovery_. Use of these codes is<br>explained in the_OCP Hardware Secure Boot White Paper_. <br>4:0 Reserved. Shall be cleared to zero.|
|SMBUS-7|The device shall take no longer than the CAP.TO timeout value to produce stable SMBus<br>output through the NVMe Basic Management Command (if supported).|
|SMBUS-8|If the device has set a non-zero value in the Panic ID field (Command Code 154, byte 01h),<br>then the device shall clear the Drive Functional field to 0b (Command Code 0, byte 01h, Bit<br>5b).|
|SMBUS-9|The device shall generate the PEC values specified for each command code in the SMBus<br>data format described inSection 11.2 - NVMe Basic Management Command (Appendix A)<br>Data Format when the host issues a Block Read.|
|SMBUS-10|<br>The device shall check the PEC value sent when the host issues a Block Write and only<br>process the message if the PEC value matches the SMBus data format specified value<br>described inSection 11.2 - NVMe Basic Management Command (Appendix A) Data Format. <br>The device is encouraged to issue a NACK if the PEC value is not correct.|
|SMBUS-11|All data returned by the NVMe Basic Management Command shall be returned in big-<br>endian format unless otherwise noted.|

### **11.2 NVMe Basic Management Command (Appendix A) Data Format**

|Command<br>Code<br>(Decimal)|Byte<br>Offset<br>(Decimal)|Description|
|---|---|---|
|0|0|Defined in the NVM Express Management Interface Specification.|
|8|8|Defined in the NVM Express Management Interface Specification.|
|32|32|Payload length of Command Code 32: This is the number of bytes until the PEC code.<br>This shall be set to 10h.|

<!-- page 171 -->
|Byte<br>Address|Value|
|---|---|
|33|73h|
|34|89h|
|35|20h|
|36|E5h|
|37|6Bh|
|38|EEh|
|39|42h|
|40|58h|
|41|9Ah|
|42|7Ah|
|43|CEh|
|44|BDh|
|45|B3h|
|46|5Fh|
|47|00h|
|48|85h|

|Command<br>Code<br>(Decimal)|Byte<br>Offset<br>(Decimal)|Description|
|---|---|---|
||48:33|GUID: This is a 16-byte Global Unique Identifier:<br>**Byte**<br>**Address**<br>**Value**<br>33<br>73h<br>34<br>89h<br>35<br>20h<br>36<br>E5h<br>37<br>6Bh<br>38<br>EEh<br>39<br>42h<br>40<br>58h<br>41<br>9Ah<br>42<br>7Ah<br>43<br>CEh<br>44<br>BDh<br>45<br>B3h<br>46<br>5Fh<br>47<br>00h<br>48<br>85h|
||49|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data. The algorithm is defined in the SMBus<br>Specification.|
|50|50|Payload length of Command Code 50: Indicated the number of additional bytes to<br>read before encountering PEC. Shall be set to 26h.|
|50|51|Temperature Flags: This field reports the effect of temperature on the device’s<br>performance.<br>Temperature Throttling – Bit 7 is set to 1b when the device is throttling performance<br>to prevent overheating. Clear to 0b when the device is not throttling.<br>Bits 6:0 shall be set to 1111111b.|
|50|52|Max Power Supported: This shall denote the Max Average Power (MAP) supported<br>by this device rounded to the nearest watt (e.g., a 50W device is 32h, a 25W device<br>is 19h, a 15W device is 0Fh, an 8.25W device is 8W which is 08h).|
|50|84:53|Configured NVMe Power State: This is a copy of the NVMe Power State Descriptor<br>Data Structure of the currently configured Power State and is laid out in little-endian<br>format.|
|50|88:85|Total NVM Capacity: This field indicates the total usable NVM capacity in the NVM<br>subsystem in GB in Hex (2048 GB in total capacity = 0000800h). This field is<br>equivalent to the TNVMCAP field in the Identify Controller Data Structure.|
|50|89|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data. The algorithm is defined in the SMBus<br>Specification.|

<!-- page 172 -->
|Bit|Bit Description|Col3|
|---|---|---|
|7|Written by host, read by device:|Written by host, read by device:|
|7|1b|Unlock Firmware Update<br>Device shall enable Firmware Image Download and<br>Firmware Commit commands both in-band and out-of-<br>band via NVMe-MI.|
|7|0b|Lock Firmware Update<br>Device shall block and error on in-band Firmware Image<br>Download and Firmware Commit commands.  The device<br>shall allow out-of-band Firmware Image Download and<br>Firmware Commit commands via NVMe-MI.|
|6|Written by device, read by host:|Written by device, read by host:|
|6|1b|Firmware Update Unlocked<br>Device allows Firmware Image Download and Firmware<br>Commit commands both in-band and out-of-band via<br>NVMe-MI.|
|6|0b|Firmware Update Locked<br>Device blocks and errors on in-band Firmware Image<br>Download and Firmware Commit commands.  The device<br>allows out-of-band Firmware Image Download and<br>Firmware Commit commands via NVMe-MI.|
|5:0|Shall be set to 111111b.|Shall be set to 111111b.|

|Command<br>Code<br>(Decimal)|Byte<br>Offset<br>(Decimal)|Description|
|---|---|---|
|90|90|Payload length of Command Code 90: Indicates number of additional bytes to read<br>before encountering PEC. Shall be set to 04h.|
|90|91|Firmware Update Flags: This field allows the host to control whether the current<br>firmware allows new firmware images to be downloaded and committed via the in-<br>band interface (seeSection 12 Security for more information).<br>**Bit**<br>**Bit Description**<br>7 <br>Written by host, read by device:<br>1b<br>Unlock Firmware Update<br>Device shall enable Firmware Image Download and<br>Firmware Commit commands both in-band and out-of-<br>band via NVMe-MI.<br>0b<br>Lock Firmware Update<br>Device shall block and error on in-band Firmware Image<br>Download and Firmware Commit commands. The device<br>shall allow out-of-band Firmware Image Download and<br>Firmware Commit commands via NVMe-MI.<br>6 <br>Written by device, read by host:<br>1b<br>Firmware Update Unlocked<br>Device allows Firmware Image Download and Firmware<br>Commit commands both in-band and out-of-band via<br>NVMe-MI.<br>0b<br>Firmware Update Locked<br>Device blocks and errors on in-band Firmware Image<br>Download and Firmware Commit commands. The device<br>allows out-of-band Firmware Image Download and<br>Firmware Commit commands via NVMe-MI.<br>5:0<br>Shall be set to 111111b.<br>The device shall revert to the default Unlock/Lock state on the next power cycle. If<br>the host attempts to issue an in-band Firmware Image Download command or<br>Firmware Commit when the device is in the Firmware Update Locked state, the<br>device shall fail the command with status Operation Denied.|
|90|94:92|Reserved. Shall be cleared to zero.|
|90|95|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data. The algorithm is defined in the SMBus<br>Specification.|
|96|96|Payload length of Command Code 96: Indicates number of additional bytes to read<br>before encountering PEC. Shall be set to 38h.|
|96|104:97|Firmware Version Number: This field shall indicate the activated firmware version<br>that is running on the device after the firmware activation took place. The format of<br>this field shall be as defined in the Firmware Revision (FR) field in the Identify<br>Controller data structure.|

<!-- page 173 -->
|Command<br>Code<br>(Decimal)|Byte<br>Offset<br>(Decimal)|Description|
|---|---|---|
||112:105|Security Version Number: This is the Security Version Number of the currently<br>running firmware image. The supplier increments this number any time a firmware<br>includes a fix for a security issue or critical firmware fix that customer agrees<br>rollback prevention is required. This is a copy ofSMART-22 – Security Version<br>Number.|
||152:113|Model Number: This shall be a copy of the data in the Model Number field of<br>Identify Controller Data Structure (CNS 01h, byte offset 63:24).|
||153|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data. The algorithm is defined in SMBus Specification.|
|154|154|Payload length of Command Code 154: Indicates number of additional bytes to read<br>before encountering PEC. Shall be set to 0Bh.|
|154|155|Panic Rest Action: SeeEREC-2.|
|154|156|Device Recovery Action 1: SeeEREC-3.|
|154|<br>164:157|<br>Panic ID: SeeEREC-4.|
|154|<br>165|<br>Device Recovery Action 2: SeeEREC-14.|
|154|<br>166|<br>PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data. The algorithm is defined in the SMBus<br>Specification.|
|167|167|Payload length of Command Code 167: Indicates number of additional bytes to read<br>before encountering PEC. Shall be set to 20h.|
|167|199:168|Panic Context Buffer: Vendor may record additional information about the Panic ID<br>reported in Command Code 154. Any unused bytes shall be cleared to zero.|
|167|200|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data. The algorithm is defined in the SMBus<br>Specification.|
|201|241:201|Reserved. Shall be cleared to zero.|
|242|242|Payload length of Command Code 242: Indicates number of additional bytes to read<br>before encountering PEC. Shall be set to 04h.|

<!-- page 174 -->
|Bit|Bit Description|
|---|---|
|7|Secure Boot Failure Feature Reporting Supported:<br>When set to 1b the secure boot feature reporting is supported.<br>When cleared to 0b the secure boot failure feature reporting is not<br>supported.|
|6|Secure Boot Failure Status:  When cleared to 0b there is no secure<br>boot failure.  When set to 1b there is a secure boot failure.  This bit<br>shall only be set if the Secure Boot Feature Supported bit is set to 1b<br>and there is a secure boot failure.|
|5|OCP Recovery/ Platform Root-of-Trust for Recovery: When set to 1b,<br>OCP Recovery/ Platform Root-of-Trust for Recovery codes are<br>supported in byte 244.  When cleared to 0b OCP Recovery/ Platform<br>Root-of-Trust for Recovery codes are not supported and byte 244<br>shall be cleared to zero.|
|4:0|Reserved.  Shall be cleared to zero.|

|Command<br>Code<br>(Decimal)|Byte<br>Offset<br>(Decimal)|Description|
|---|---|---|
||243|Secure Boot Failure Reporting:<br>Bit <br>Bit Description <br>7 <br>Secure Boot Failure Feature Reporting Supported:<br>When set to 1b the secure boot feature reporting is supported.<br>When cleared to 0b the secure boot failure feature reporting is not<br>supported.<br>6 <br>Secure Boot Failure Status:  When cleared to 0b there is no secure<br>boot failure.  When set to 1b there is a secure boot failure.  This bit<br>shall only be set if the Secure Boot Feature Supported bit is set to 1b<br>and there is a secure boot failure.<br>5 <br>OCP Recovery/ Platform Root-of-Trust for Recovery: When set to 1b,<br>OCP Recovery/ Platform Root-of-Trust for Recovery codes are<br>supported in byte 244.  When cleared to 0b OCP Recovery/ Platform<br>Root-of-Trust for Recovery codes are not supported and byte 244<br>shall be cleared to zero.<br>4:0 Reserved.  Shall be cleared to zero.|
||244|Recovery Code: OCP Recovery/Platform Root-of-Trust for Recovery code.|
||246:245|Reserved.  Shall be cleared to zero.|
||247|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data.  The algorithm is defined in the SMBus<br>Specification.|
|248|248|Payload length of Command Code 248: Indicates number of additional bytes to read<br>before encountering PEC.  Shall be set to 06h.|
|248|250:249|Data Format Version Number: Indicates the version of this mapping used in the<br>device.  Shall be set to 0004h.|
|248|254:251|Reserved.  Shall be cleared to zero.|
|248|255|PEC: An 8-bit CRC calculated over the SMBus address, command code, second<br>SMBus address and returned data.  The algorithm is defined in the SMBus<br>Specification.|

### **11.3 NVMe-MI Requirements**

|Requirement ID|Description|
|---|---|
|NVMe-MI-1|The device shall support NVM Express Management Interface Specification, Revision 2.0 or<br>later, including all mandatory requirements.  The vendor shall provide an NVMe-MI<br>compliance report that demonstrates compliance.|
|NVMe-MI-2|The device shall support all NVMe-MI functionality required by this specification over<br>SMBus, even when the PCIe link is not active (as required by the NVM Express<br>Management Interface Specification).|
|NVMe-MI-3|The device shall support NVMe-MI over PCIe VDM (see NVMe-MI-1).|
|NVMe-MI-4|The device shall support SMBus Fixed and Discoverable.|

<!-- page 175 -->
|Requirement ID|Description|
|---|---|
|NVMe-MI-5|The device shall NACK any SMBus addresses not listed in the NVM Express Management<br>Interface Specification.|
|NVMe-MI-6|The device shall support the Get UDID command per the SMBus Specification.|
|NVMe-MI-7|Obsolete, seeFRU-1.|
|NVMe-MI-8|Obsolete, see NVMe-MI-2.|
|NVMe-MI-9|Obsolete, see NVMe-MI-3.|
|NVMe-MI-10|All mandatory NVMe Admin commands and the following optional NVMe Admin<br>commands shall be supported by MCTP over SMBus, and by MCTP over PCIe VDM.<br>• <br>Firmware Commit<br>• <br>Firmware Image Download<br>• <br>Format NVM<br>• <br>Lockdown<br>• <br>Sanitize<br>• <br>Security Send for TCG devices<br>• <br>Security Receive for TCG devices<br>• <br>Device Self-test<br>• <br>Set Features|
|NVMe-MI-11|All mandatory Log Identifiers and the following optional Log Identifiers shall be supported<br>by MCTP over SMBus, and by MCTP over PCIe VDM.<br>• <br>Device Self-test (06h)<br>• <br>Command and Feature Lockdown (14h)<br>• <br>Sanitize Status (81h)<br>• <br>SMART / Health Information Extended (C0h)|
|NVMe-MI-12|The following Log Identifiers shall be supported by MCTP over SMBus, and by MCTP over<br>PCIe VDM.<br>• <br>Persistent Event Log (0Dh)<br>• <br>Telemetry Host-Initiated (07h)<br>• <br>Telemetry Controller-Initiated (08h)|
|NVMe-MI-13|The following Feature Identifiers shall be supported by MCTP over SMBus, and by MCTP<br>over PCIe VDM.<br>• <br>Power Management (02h)<br>• <br>Timestamp (0Eh)<br>• <br>Temperature Threshold (04h)|
|NVMe-MI-14|The device shall support locking down all supported Admin commands and all supported<br>Features on the in-band interface via a Lockdown command issued out-of-band via MCTP<br>over SMBus, and by MCTP over PCIe VDM. This includes the Lockdown command itself<br>and all Admin commands and Features not referenced in this specification.|

<!-- page 176 -->
|Requirement ID|Description|
|---|---|
|NVMe-MI-15|The following commands are prohibited and shall return an NVMe-MI Response Message<br>Status of Invalid Command Opcode:<br>• <br>PCIe Memory Write<br>• <br>PCIe Memory Read<br>• <br>PCIe I/O Write<br>• <br>PCIe I/O Read<br>Support for the PCIe Configuration Read command is optional.|
|NVMe-MI-16|Access to user data is prohibited via out-of-band NVMe-MI (e.g., vendor-specific<br>commands shall not access user data).|
|NVMe-MI-17|The device shall support SMBus/I2C Frequencies of 100 KHz and 400 KHz.|
|NVMe-MI-18|For SMBus, the device shall support all possible MCTP Transmission Unit Size values up to<br>the largest (250 bytes).|
|NVMe-MI-19|For PCIe VDM, the NVMe device shall support all possible MCTP Transmission Unit Size<br>values up to the PCIe Max Payload Size Supported.|
|NVMe-MI-20|NVMe devices shall support a minimum throughput of 50 MiB/s for reads and writes for<br>the MCTP over PCIe VDM interface under the assumption that there is no delay between<br>Request Messages from the Management Controller for transfers that require multiple<br>Request/Response Messages.|
|NVMe-MI-21|Any TCG method invoked via NVMe-MI that takes longer than 100 ms shall run in the<br>background using the OutstandingData mechanism (preferred) or the More Processing<br>Required mechanism.|
|NVMe-MI-22|The device shall support NVMe-MI over SPDM Secured Messages (seeSPDM-7).|
|<br>NVMe-MI-23|<br>The device shall support the following Asynchronous Event Messages per TP6035a and<br>shall support the following Asynchronous Events:<br>• <br>Controller Fatal Status (Asynchronous Event ID 01h)<br>• <br>Shutdown Status (Asynchronous Event ID 02h)<br>• <br>Namespace Attribute Changed (Asynchronous Event ID 04h)<br>• <br>Firmware Activated (Asynchronous Event ID 05h)<br>• <br>Composite Temperature (Asynchronous Event ID 06h)<br>• <br>Percentage Drive Life Used (Asynchronous Event ID 07h)<br>• <br>Available Spare (Asynchronous Event ID 08h)<br>• <br>SMART Warnings (Asynchronous Event ID 09h)<br>• <br>Telemetry Controller-Initiated Data Available (Asynchronous Event ID 0Ah)<br>• <br>PCIe Link Active (Asynchronous Event ID 0Bh)<br>• <br>Sanitize Failure Mode (Asynchronous Event ID 0Ch)|
|NVMe-MI-24|If the SMBus clock is low for longer than tTIMEOUT,MIN (refer to the SMBus Specification), then<br>the device shall perform SMBus clock-low recovery even if firmware is hung.|
|NVMe-MI-25|The device shall support retrieval of log pages greater than 4 KiB as required by the NVM<br>Express Management Interface Specification.|
|NVMe-MI-26|For devices that support auxiliary power, the device shall be fully functional including<br>NVMe-MI over SMBus/I2C as long as main power is present.|
|NVMe-MI-27|The device shall support I3C Basic as specified in the NVM Express Management Interface<br>Specification for form factors that support I3C.|

<!-- page 177 -->
|Requirement ID|Description|
|---|---|
|NVMe-MI-28|The device shall support the PCIe Configuration Write command for a single-byte-sized<br>PCIe Configuration Write to the Power Management Control/Status Register (Offset 04h)<br>in the PCI Power Management Capability Structure. PCIe Configuration Writes to any<br>register other than the Power Management Control/Status Register shall be aborted with a<br>status code of Access Denied.|

### **11.4 VPD Requirements**

|Requirement ID|Description|
|---|---|
|FRU-1|The device shall have a VPD that is accessible over SMBus and supports IPMI Platform<br>Management FRU Information. The VPD shall support all required elements that are<br>defined in the NVM Express Management Interface Specification.|
|FRU-2|The device shall support a FRU Information Device Size of at least 512 bytes.|
|FRU-3|The device shall support the NVMe MultiRecord (i.e., Record Type ID 0Bh). The length of<br>MultiRecord shall be set to 20h to remove reserved bytes.|
|FRU-4|The device shall support the NVMe PCIe MultiRecord (i.e., Record Type ID 0Ch). The length<br>of MultiRecord shall be set to 8h to remove reserved bytes.|
|FRU-5|The device shall support the following Topology MultiRecords (i.e., Record Type ID 0Dh):<br>• <br>Upstream Connector Element Descriptor (i.e., Element Descriptor Type 2h);<br>• <br>NVM Subsystem Element Descriptor (i.e., Element Descriptor Type 7h); and<br>• <br>FRU Information Device Element Descriptor (i.e., Element Descriptor Type 8h).|
|FRU-6|The Maximum Power field in the Upstream Connector Element Descriptor shall indicate<br>maximum average power measured required byPCM-1.|

## **12 Security**

### **12.1 Basic Security Requirements**

|Requirement ID|Description|
|---|---|
|SEC-1|The device shall support signed firmware binary update which is checked when the device<br>processes the Firmware Commit command and when firmware is activated. The device<br>firmware shall be authenticated using cryptographic keys on every reboot and during<br>firmware update.|
|SEC-2|The device shall support XTS-AES-256 (as specified in NIST SP 800-38E, which references<br>IEEE STD 1619) or AES-256-GCM (as specified in NIST SP 800-38D) hardware-based data<br>encryption for performance and to prevent firmware tampering with the encryption<br>mechanism. AES-256-GCM is the preferred mode.<br>The combination of AES-256-CTR (as specified in NIST SP 800-38A) with HMAC-SHA256<br>(where the HMAC is calculated on the ciphertext) is an acceptable alternative.|

<!-- page 178 -->
|Requirement ID|Description|
|---|---|
|SEC-3|The device shall support anti-rollback protection for firmware. If the Security Version<br>Number (seeSMART-22) of the firmware being committed or activated is greater or equal<br>to the Security Version Number of the currently running firmware, then the firmware is<br>allowed to be committed or activated. If the Security Version Number of the firmware<br>being committed or activated is less than the Security Version Number of the currently<br>running firmware, then the firmware update shall be aborted with a status code of<br>Firmware Activation Prohibited and the firmware shall not be committed or activated.|
|SEC-4|The device shall support Crypto Erase (seeNVMe-AD-5) andNVMe-AD-7).|
|<br>SEC-5|<br>The device shall support Secure Boot (seeSection 12.2 Secure Boot).|
|SEC-6|The device shall have a method of identifying a secure boot failure which does not require<br>physical access to the device.|
|SEC-7|The device’s cryptographic module shall be FIPS 140-3 level 2 capable per CMVP and shall<br>follow the NIST 800-90 (A, B and C) specification.|
|SEC-8|The device shall only implement NIST approved cryptographic algorithms and shall be<br>designed to achieve FIPS-140-3 validation (see SEC-7).|
|SEC-9|The device shall support key revocation allowing a new key to be used for firmware<br>verification. The device shall support at least 4 key revocations, and key revocation shall<br>not make the device unbootable (i.e., the device supports at least 5 keys).|
|SEC-10|Obsolete. Moved toTCG-FEATURE-1.|
|<br>SEC-11|<br>Obsolete. Moved toTCG-FEATURE-2.|
|<br>SEC-12|<br>Obsolete. Moved toTCG-FEATURE-3.|
|<br>SEC-13|<br>TCG devices shall support the IEEE1667 Probe (100h) and the TCG Storage Transport<br>(104h) silos. See SEC-50 and SEC-51 for additional IEEE1667 requirements.|
|SEC-14|Supplier shall follow the Security Development Lifecycle (SDL), and provide a report with<br>the following for each qualification-ready or production-ready firmware version:<br>• <br>The Threat Model.<br>• <br>Fuzz & Pen Tests.<br>• <br>Static Analysis.<br>• <br>Build Logs and Compiler Security Settings.<br>Additional information about the SDL is available here:<br>_https://www.microsoft.com/en-us/sdl/default.aspx_|
|SEC-15|<br>A firmware audit of the initial firmware released to customer intended for qualification<br>and any subsequent firmware release intended for production use shall be performed<br>using_OCP SAFE_, Framework V1.0 or later. Each detailed report shall be provided to the<br>customer.|
|SEC-16|All signing keys shall be stored in a Hardware Security Module (HSM) that is either FIPS<br>140-2 Level 3 (or greater) certified or FIPS 140-3 Level 3 (or greater) certified.|
|SEC-17|Access/use of signing keys should be restricted to a small set of developers, following the<br>principle of least privilege. The number of people with access and their corresponding<br>roles shall be provided.|
|SEC-18|All debug ports shall be disabled before the device leaves the factory. Alternatively, the<br>ports shall only be accessible in the field after a successful exchange of a challenge-<br>response mechanism using an asymmetric crypto scheme (see NIST SP 800-63). The state<br>shall be reset to inaccessible on any reset or power cycle.|

<!-- page 179 -->
|Requirement ID|Description|
|---|---|
|SEC-19|All vendor unique commands, log pages or set features that are not explicitly defined in<br>this specification or approved of in writing by the customer shall be disabled before the<br>device leaves the factory. Alternatively, the commands/log pages/set features shall only<br>be accessible in the field after a successful exchange of a challenge-response mechanism<br>using an asymmetric crypto scheme (see NIST SP 800-63). The state shall be reset to<br>inaccessible on any reset or power cycle.|
|SEC-20|Adversarial testing using red teams shall be conducted before the start of customer<br>qualification of the initial SSD product and any major firmware or hardware revision. A<br>report of items attempted, and results shall be provided to the customer.|
|SEC-21|The vendor shall provide timely notification to the customer of security issues and delivery<br>of fixes to the customer:<br>● The vendor shall document all security fixes with each firmware update.<br>● The vendor shall notify end customer within 7 days of discovering security issues in the<br>device hardware or firmware.<br>● Notification of issues shall include the process and timeline of the vendor’s<br>commitment to fix the issue:<br>`o` For privately disclosed vulnerabilities, the duration shall be no longer than 90 days.<br>`o` For publicly disclosed vulnerabilities, the duration shall be no longer than 7 days.<br>`o` Vendors shall notify the customers about the known CVEs and security issues and<br>provide security-related updates before public announcement.|
|SEC-22|The Telemetry Controller-Initiated log page, Telemetry Host-Initiated log page, shall be<br>designed to be human readable, except for Telemetry Data Areas 3 and 4. The contents of<br>Data Area 1 and Data Area 2 shall be sufficient to debug.|
|SEC-23|The device shall not include user data, passwords, keys, or any secret or sensitive<br>information in any Telemetry or debug log pages.|
|SEC-24|All public keys shall be revocable.|
|SEC-25|Secure Boot Flow shall be based upon a hardware root of trust. All mutable key(s),<br>certificate(s), and/or firmware shall be cryptographically bound to the hardware root of<br>trust. SeeSection 12.2 Secure Boot.|
|SEC-26|<br>The device shall only update firmware via a secure firmware update flow that shall be<br>based upon immutable public keys.|
|SEC-27|Obsolete. Moved toTCG-CRYPTO-1.|
|<br>SEC-28|<br>The device shall purge all symmetric keys and all private asymmetric keys from volatile<br>memory as soon as they are no longer needed for operation during the current power on<br>state.|
|SEC-29|The device shall only store, even if temporarily, host provided passwords, host provided<br>keys, or any host provided secret information in non-volatile memory in an encrypted<br>form. The encryption key(s) for this protection shall not be stored in non-volatile memory.<br>Device shall not store plaintext/cleartext secrets in any non-volatile memories. The device<br>shall protect all such stored passwords, keys, and secrets from unauthorized modification.|

<!-- page 180 -->
|Requirement ID|Description|
|---|---|
|SEC-30|The supplier must deliver key management and encryption flow diagram details (not<br>source code) which includes:<br>• <br>Encryption algorithms and modes (e.g., RNG, wrapping function, key derivation<br>function).<br>• <br>Key size and password length.<br>• <br>Any crypto information that is stored in nonvolatile memory.<br>• <br>Critical Security Parameters.<br>Complete details about algorithm inputs (e.g., Initialization vector source and size, salt<br>source and size, unique per device/product line/vendor)|
|SEC-31|The supplier must provide industry certification reports, if available, such as FIPS, NIST for<br>device and device components such as TRNG, RNG, Crypto engine etc.|
|SEC-32|Log data and user data (data transferred from the Host in Write Commands) shall be<br>stored on physically separate areas on the device. For example, in the system area and the<br>user data area, respectively.|
|SEC-33|The vendor shall provide a comprehensive list of what is included in the logs covering both<br>the standard logs and vendor-unique logs. The list shall identify any defined optional<br>events or items that are not logged by the device.|
|SEC-34|Obsolete.|
|SEC-35|All telemetry and debug logs shall only be writable by device firmware that has been<br>verified as part of a secure boot.|
|SEC-36|Obsolete. Moved toTCG-AUTH-3.|
|<br>SEC-37|<br>Obsolete. Moved toNVME-MI-2 andNVME-MI-10.|
|<br>SEC-38|<br>Obsolete. Moved toTCG-FEATURE-4.|
|SEC-39|The device shall not allow the host to read firmware or boot code from the device.|
|SEC-40|All device firmware packages shall be encrypted based on a symmetric encryption<br>algorithm. See SEC-2 for acceptable algorithms and SEC-29 for key storage requirements.|
|SEC-41|The device shall only support activation of encrypted firmware images.|
|SEC-42|The device shall only store firmware in encrypted format when stored in non-volatile<br>memory.|
|SEC-43|Sanitize, Format NVM User Data Erase/Cryptographic Erase, and TCG<br>Revert/RevertSP/GenKey shall comply with the IEEE 2883-2022 Purge requirements.|
|SEC-44|Any command that changes the media encryption key(s) as part of its operation (e.g.,<br>Sanitize command with Crypto Erase (100b), TCG Revert, TCG RevertSP, etc.), shall purge,<br>as defined in IEEE 2883-2022, all copies of the previous key(s) before the device completes<br>the operation. If the device cannot guarantee that all copies of the previous media<br>encryption key(s) have been purged, then the device shall fail the operation.|
|SEC-45|Any optional security features supported by the device and not described in this document<br>shall be clearly documented and disclosed to the customer.|
|SEC-46|TCG devices shall support the Security Receive and Security Send commands in-band (i.e.,<br>bit 0 in the Optional Admin Command Support field in the Identify Controller data<br>structure shall be set to 1b).|

<!-- page 181 -->
|Requirement ID|Description|
|---|---|
|SEC-47|The Cryptographic Module Boundary should be defined to minimize the size and scope of<br>the Cryptographic Module, and in particular the Cryptographic Module Boundary should<br>not encompass the entire physical device.  This enables FIPS certification of the<br>Cryptographic Module to be leveraged across multiple device configurations and versions.<br>To facilitate a timelier NIST certification approval process, any revalidations made to the<br>Cryptographic Module Boundary should be Non-Security Relevant.  The Cryptographic<br>Module Boundary shall include all relevant cryptographic functions within the boundary<br>itself, such as the data at rest encryption algorithms per FIPS 197 and digital signature<br>algorithms for firmware authentication per FIPS 186-5.|
|SEC-48|At a minimum, the device shall support the following signature and hashing algorithms for<br>secure boot, firmware update, CoRIM, and SPDM implementations:<br>• <br>ECDSA P384 or other asymmetric key signature algorithms that meet at least<br>192-bits of security strength as documented in NIST SP 800-57 Part 1 Revision 5<br>(Table 2).  The device may also support RSA 3072 instead.<br>• <br>SHA-384, SHA3-384 or other hashing algorithms that meet at least 192-bits of<br>security strength as documented in NIST SP 800-57 Part 1 Revision 5 (Table 3).|
|SEC-49|The device shall not reveal secrets (including passwords, asymmetric private keys,<br>symmetric keys, and any other secret information) even in encrypted form via<br>programmatic methods, logging operations (including debug outputs), and within<br>externally accessible configuration files or settings.|
|SEC-50|After power on, for a given ComID, any IEEE1667 functionality that is different than what is<br>specified by the TCG specifications (e.g., the Command Sequencing Reset differences) shall<br>only take effect if IEEE1667 support is enabled (see G1667-2) and the device receives a<br>Security Send or Security Receive command with the Security Protocol field set to a value<br>of EEh on that ComID only (i.e., IEEE1667).<br>Once the device receives a Security Send or Security Receive command with the Security<br>Protocol field set to a value of EEh on a given ComID, then the device shall behave as<br>specified by the IEEE1667 Specification for that ComID until the next Controller Level Reset<br>when the device shall switch back to TCG-compliant behavior for all ComIDs.|
|SEC-51|If IEEE1667 support is enabled and the host completes taking ownership of the device<br>(refer to the TCG Storage Application Note: Encrypting Drives Compliant with Opal SSC) via<br>the Security Send/Security Receive commands with the Security Protocol field set to a<br>value of 01h to 06h (i.e., TCG), then the device shall go into a mode where Security Send or<br>Security Receive command with the Security Protocol field set to a value of EEh is<br>prohibited and results in an error status code of Access Denied being returned for any<br>Security Send or Security Receive command with the Security Protocol field set to a EEh.<br>If the device is in the mode where Security Send or Security Receive command with the<br>Security Protocol field set to a value of EEh is prohibited, then a Revert shall cause the<br>device to switch back to a mode where Security Send or Security Receive command with<br>the Security Protocol field set to a value of EEh is allowed.|

### **12.2 Secure Boot**

The device shall support Secure Boot. There are two fundamental things to address for secure boot:

<!-- page 182 -->
- Secure boot rooted in hardware.

  - Core Root of Trust Measurement.

The vendor should follow the recommendations in the _[TCG Hardware Requirements for a Device Identifier](https://trustedcomputinggroup.org/wp-content/uploads/Hardware-Requirements-for-Device-Identifier-Composition-Engine-r78_For-Publication.pdf)_
_[Composition Engine](https://trustedcomputinggroup.org/wp-content/uploads/Hardware-Requirements-for-Device-Identifier-Composition-Engine-r78_For-Publication.pdf)_ and the guidelines in NIST SP 800-193. DICE coupled with _[TCG Implicit Identity Based](https://trustedcomputinggroup.org/wp-content/uploads/TCG-DICE-Arch-Implicit-Identity-Based-Device-Attestation-v1-rev93.pdf)_
_[Device Attestation](https://trustedcomputinggroup.org/wp-content/uploads/TCG-DICE-Arch-Implicit-Identity-Based-Device-Attestation-v1-rev93.pdf)_ and Source for _[RIoT Reference Architecture](https://github.com/microsoft/RIoT)_ can help implement Cryptographic Identity
with implicit attestation.

|Requirement ID|Description|
|---|---|
|SBT-1|The device shall comply with the_FIPS 186-5 Digital Signature Standard (DSS)_ or later and<br>the_OCP Hardware Secure Boot V1.0_. This requirement does not require the full<br>implementation of the OCP Recovery specification, only the Recover Error Codes (see<br>SMBUS-6). This requirement does not require implementation of the OCP Attestation of<br>System Components specification.|
|SBT-2|For Core Root of Trust measurement, each device shall have a Cryptographic Device<br>Identity.|
|SBT-3|The_TCG Hardware Requirements for a Device Identifier Composition Engine V1.0 R0.91 or_<br>_later_ standard or an alternative hardware based cryptographic identity shall be<br>implemented.|
|SBT-4|The device shall implement at least one of the Digital Signature PQC algorithms as<br>specified in the_Commercial National Security Algorithm Suite 2.0_ no later than 2025.|
|SBT-5|Secure boot flow shall be immutable for exploitation and use immutable public keys.|

### **12.3 DMTF Security Protocol and Data Model (SPDM)**

The vendor should follow the guidelines in NIST SP 800-193.

|Requirement ID|Description|
|---|---|
|SPDM-1|The device shall comply with the Security Protocol and Data Model (SPDM) Specification,<br>Version 1.2.2 or later. The device shall be backwards compatible with the Security<br>Protocol and Data Model (SPDM) Specification, Version 1.1 and later.|
|SPDM-2|The device shall comply with the revised PCI-SIG Component Measurement and<br>Authentication (CMA-SPDM) ECN that was published on September 20, 2023.|
|SPDM-3|The device shall support SPDM-1 and SPDM-2 via MCTP over SMBus/I2C.|
|SPDM-4|The device shall support SPDM-1 and SPDM-2 via MCTP over PCIe VDM.|
|SPDM-5|The device shall support SPDM-1 and SPDM-2 via PCI-SIG Data Object Exchange (DOE)<br>Revision 1.1.|
|SPDM-6|Obsolete. SeeCERT-1.|
|<br>SPDM-7|<br>The device shall comply with the Secured Messages using SPDM over MCTP Binding<br>Specification, Version 1.1.1 or later.|
|SPDM-8|The device shall comply with the Secured Messages using SPDM Specification, Version<br>1.1.1 or later. Mutual authentication is not required.|
|SPDM-9|The device shall comply with the Security Protocol and Data Model (SPDM) over MCTP<br>Binding Specification, Version 1.0.2 or later.|
|SPDM-10|The device shall not drop the response if the device does not receive RESPOND_IF_READY<br>within WTMax amount of time after sending an ERROR message with an ErrorCode equal to<br>ResponseNotReady.|

<!-- page 183 -->
|Requirement ID|Description|
|---|---|
|SPDM-11|The device shall be ready to respond to SPDM requests within a maximum of 2 second<br>after main power is applied.|
|SPDM-12|The device’s SPDM MCTP interpacket delay shall be less than 40 ms.|
|SPDM-13|The device shall have a unique and immutable hardware identity based on an asymmetric<br>key pair, and DeviceCert that includes hardware identity information as defined in the<br>SPDM Specification.|
|SPDM-14|The device shall support a DataTransferSize of at least 4 KiB.|
|SPDM-15|The device shall comply with the SPDM requirements in the following table:<br>**Response**<br>**Code**<br>**Requirement**<br>DIGESTS<br>01h<br>Required<br>CERTIFICATE<br>02h<br>Required<br>CHALLENGE_AUTH<br>03h<br>Required<br>VERSION<br>04h<br>Required<br>CHUNK_SEND_ACK<br>05h<br>Optional<br>CHUNK_RESPONSE<br>06h<br>Optional<br>MEASUREMENTS<br>60h<br>Required<br>CAPABILITIES<br>61h<br>Required<br>ALGORITHMS<br>63h<br>Required<br>KEY_EXCHANGE_RSP<br>64h<br>Required<br>FINISH_RSP<br>65h<br>Required<br>PSK_EXCHANGE_RSP<br>66h<br>Optional<br>PSK_FINISH_RSP<br>67h<br>Optional<br>HEARTBEAT_ACK<br>68h<br>Optional<br>KEY_UPDATE_ACK<br>69h<br>Required<br>ENCAPSULATED_REQUEST<br>6Ah<br>Required<br>ENCAPSULATED_RESPONSE_ACK<br>6Bh<br>Required<br>END_SESSION_ACK<br>6Ch<br>Required<br>CSR<br>6Dh<br>Recommended<br>SET_CERTIFICATE_RSP<br>6Eh<br>Recommended<br>VENDOR_DEFINED_RESPONSE<br>7Eh<br>Optional<br>ERROR <br>7Fh<br>Required|
|SPDM-16|The device shall comply with the CHALLENGE_AUTH response requirements in the<br>following table:<br>CHALLENGE_AUTH Response<br>Requirement<br>0h = No Measurement Summary Hash<br>Required<br>1h = TCB Component Measurement Hash<br>Required<br>FFh = All measurements Hash<br>Required|
|SPDM-17|Signature endianness shall follow the requirements in Security Protocol and Data Model<br>(SPDM) Specification, Version 1.2.2 or later even in the case that an older SPDM version is<br>supported by the device. For example, on ECDSA signatures, the byte order for r and s<br>shall be big endian order. When placing ECDSA signatures into an SPDM signature field, r<br>shall come first, followed by s.|

|Response|Code|Requirement|
|---|---|---|
|DIGESTS|01h|Required|
|CERTIFICATE|02h|Required|
|CHALLENGE_AUTH|03h|Required|
|VERSION|04h|Required|
|CHUNK_SEND_ACK|05h|Optional|
|CHUNK_RESPONSE|06h|Optional|
|MEASUREMENTS|60h|Required|
|CAPABILITIES|61h|Required|
|ALGORITHMS|63h|Required|
|KEY_EXCHANGE_RSP|64h|Required|
|FINISH_RSP|65h|Required|
|PSK_EXCHANGE_RSP|66h|Optional|
|PSK_FINISH_RSP|67h|Optional|
|HEARTBEAT_ACK|68h|Optional|
|KEY_UPDATE_ACK|69h|Required|
|ENCAPSULATED_REQUEST|6Ah|Required|
|ENCAPSULATED_RESPONSE_ACK|6Bh|Required|
|END_SESSION_ACK|6Ch|Required|
|CSR|6Dh|Recommended|
|SET_CERTIFICATE_RSP|6Eh|Recommended|
|VENDOR_DEFINED_RESPONSE|7Eh|Optional|
|ERROR|7Fh|Required|

|CHALLENGE_AUTH Response|Requirement|
|---|---|
|0h = No Measurement Summary Hash|Required|
|1h = TCB Component Measurement Hash|Required|
|FFh = All measurements Hash|Required|

<!-- page 184 -->
|Requirement ID|Description|
|---|---|
|SPDM-18|A device that is not ready to accept a new request message shall respond with an ERROR<br>response message with an ErrorCode of Busy (3h) (i.e., the device shall not silently discard<br>the request message).<br> <br>This requirement does not apply while a device is becoming ready to respond to SPDM<br>requests after application of main power (see SPDM-11).|
|SPDM-19|If a request is received out of order, then the device shall respond with an ERROR response<br>message with an ErrorCode of RequestResynch (i.e., 43h) for that request and for all<br>subsequent requests until a GET_VERSION command is received and processed (i.e., the<br>device shall not silently discard requests due to an out of order request).|

**12.3.1 SPDM Certificates**

|Requirement ID|Description|
|---|---|
|CERT-1|The leaf certificate shall include a Subject Alternative Name certificate extension<br>otherName field using the DMTF OID as defined in the Security Protocol and Data Model<br>(SPDM) Specification with the following settings:<br>• <br>the DMTF-serialNumber shall be set to same value reported in the Serial Number<br>field of the Identify Controller data structure;<br>• <br>the DMTF-product shall be set to same value reported in the Model Number field<br>of the Identify Controller data structure; and<br>• <br>the DMTF-manufacturer shall be set to a value reported in the PCI Vendor ID field<br>using the ASCII representation of the hexadecimal value without a leading “0x” or<br>trailing “h”.|
|CERT-2|The Root CA Trusted Certificate Authority shall be the device vendor and shall be the same<br>across all device models developed by the device vendor.|
|CERT-3|Device self-signed certificates are prohibited.|
|CERT-4|The device shall support the AliasCert or DeviceCert model in slot 0.  An AliasCert in slot 0<br>is permitted while running regardless of which version of the SPDM Specification is<br>negotiated (e.g., AliasCert in slot 0 is permitted running in SPDM 1.1 mode).|
|CERT-5|The AliasCert chain shall contain an immutable hardware identity certificate and hardware<br>identity OID (refer to the SPDM Specification) shall be used to indicate hardware identity<br>certificate(s).|
|CERT-6|A Mutable certificate OID (refer to the SPDM Specification) shall be used to indicate<br>mutable certificates.|

<!-- page 185 -->
**12.3.2 SPDM Firmware Measurements**

|DMTFSpecMeasurementValueType|Requirement|
|---|---|
|[7] - 0b: Digest, 1b: Raw Bit Stream|Digest<br>Required|
|[6:0] = 00h: immutable ROM|Recommended|
|[6:0] = 01h: mutable firmware|Required|
|[6:0] = 02h: hardware configuration, such as straps, debug modes|Recommended|
|[6:0] = 03h: firmware configuration (e.g., configurable firmware policy)|Recommended|
|[6:0] = 04h: Measurement manifest|Required|
|[6:0] = 05h: Structured representation of debug and device mode|Optional|
|[6:0] = 06h: Mutable firmware’s version number|Optional|
|[6:0] = 07h: Mutable firmware’s security version number, which should<br>be formatted as an 8-byte unsigned integer|Optional|

|Requirement ID|Description|
|---|---|
|SFM-1|The device shall be able to generate signed measurements (i.e., MEAS_CAP field shall be<br>set to 10b) and shall support the following Measurement block types:<br>**DMTFSpecMeasurementValueType**<br>Requirement <br>[7] - 0b: Digest, 1b: Raw Bit Stream<br>Digest<br>Required<br>[6:0] = 00h: immutable ROM<br>Recommended<br>[6:0] = 01h: mutable firmware<br>Required<br>[6:0] = 02h: hardware configuration, such as straps, debug modes<br>Recommended<br>[6:0] = 03h: firmware configuration (e.g., configurable firmware policy)<br>Recommended<br>[6:0] = 04h: Measurement manifest<br>Required<br>[6:0] = 05h: Structured representation of debug and device mode<br>Optional<br>[6:0] = 06h: Mutable firmware’s version number<br>Optional<br>[6:0] = 07h: Mutable firmware’s security version number, which should<br>be formatted as an 8-byte unsigned integer<br>Optional|
|SFM-2|The device shall always return measurements of the most recently activated firmware and<br>current configuration without requiring a power cycle or any type of NVMe or PCIe reset.<br>Measurements of the activated firmware image are acceptable.|
|SFM-3|The device shall report the same measurements blocks and values for all devices in a<br>product family (e.g., devices with the same model but different capacity points,<br>endurance, or form factor).|
|SFM-4|The device shall provide a reference integrity measurement manifest (RIM) for the<br>firmware modules and configuration settings for components using the CoRIM schema as<br>defined by IETF (refer to the latest version ofdraft-ietf-rats-corim - Concise Reference<br>Integrity Manifest or the RFC (if any) published from that Internet-Draft).|
|SFM-5|<br>The reference measurements in the CoRIM schema may be expressed using the CoMID<br>tags and/or the CoSWID tags. If the CoRIM has reference measurements from sub-<br>components from different manufacturers, then the reference values of the sub-<br>components shall be captured in CoSWID tags with their individual signatures.|
|SFM-6|The RIM shall apply to all devices in a product family (e.g., devices with the same model<br>but different capacity points, endurance, or form factor). The RIM shall not include any<br>instance specific information (e.g., any device specific identifiers such as Serial Number,<br>UUID, etc.).|
|SFM-7|The RIM shall be signed by the device manufacturer using the COSE schema (refer toRFC <br>8152 - CBOR Object Signing and Encryption (COSE) (ietf.org)). The device manufacturer<br>shall use an approved digital signature algorithm (seeSEC-48).|
|SFM-8|The device manufacturer shall provide the customer with a digital certificate with the<br>public key that is able to be used to verify the RIM signatures. This digital certificate shall<br>validate (e.g., via direct signature or certificate chain) to the Root CA Trusted Certificate<br>Authority (see CERT-2).|

<!-- page 186 -->
|Requirement ID|Description|
|---|---|
|SFM-9|The RIM shall contain the hash values of each firmware module using an approved hashing<br>algorithm (seeSEC-48).  ASCII text string values in the RIMs are acceptable if the string<br>length is less than 128 bytes and the string is descriptive (e.g., a module identifier string, a<br>product identifier string, or firmware revision string).|

### **12.4 Data Encryption and Eradication**

|Requirement ID|Description|
|---|---|
|DATAE-1|Obsolete. Duplicate ofSEC-2.|

### **12.5 TCG Implementation Requirements**

Devices that support TCG functionality (i.e., TCG devices) shall implement the specifications in accordance
with the additional requirements in this section.

|Feature/Parameters|Col2|Value|
|---|---|---|
|SSC Feature Descriptor|SSC Feature Descriptor|Opal 2 (0203h)|
|TCG Storage Architecture Core Specification|TCG Storage Architecture Core Specification|Version 2.01, Revision 1.00|
|SID|# of SIDs|1 <br>(SeeTCG-FEATURE-1)|
|SID|TryLimit|<br>10<br>(SeeTCG-AUTH-3)|
|SID|Persistence|<br>FALSE<br>(SeeTCG-AUTH-5)|
|Number of Locking<br>SP|Admin authorities|4 (min)<br>(SeeTCG-LOCKING-6)|
|Number of Locking<br>SP|User authorities|<br>8 (min)<br>(SeeTCG-LOCKING-1 and<br>TCG-LOCKING-2)|
|Number of Locking<br>Ranges|Global|1 <br>(SeeTCG-FEATURE-1)|
|Number of Locking<br>Ranges|Additional|<br>8 (min)<br>(SeeTCG-LOCKING-1)|
|DataStore size|DataStore size|10 MiB (min)<br>(SeeTCG-FEATURE-1)|
|MBR Table|MBR Table|<br>Mandatory|
|Configurable Access Control|Configurable Access Control|Mandatory<br>(SeeTCG-FEATURE-1)|
|Life Cycle support|Life Cycle support|Mandatory<br>(SeeTCG-FEATURE-1)|
|Repurpose (Revert/ Revert SP)|Repurpose (Revert/ Revert SP)|Mandatory<br>(SeeTCG-FEATURE-1)|
|Shadow MBR|Shadow MBR|Mandatory<br>(and disabled by default)|
|Feature Sets|Single User Mode|Mandatory<br>(SeeTCG-FEATURE-2)|

<!-- page 187 -->
|Feature/Parameters|Col2|Value|
|---|---|---|
||PSK Secure Messaging|Optional|
||PSID|Mandatory<br>(SeeTCG-FEATURE-1)|
||Block SID|<br>Mandatory<br>(SeeTCG-FEATURE-1)|
||Additional Data Store Tables|Mandatory<br>(SeeTCG-FEATURE-7)|

**12.6.1 TCG Version and Features**

|Requirement ID|Description|
|---|---|
|TCG-FEATURE-1|TCG devices shall support TCG Storage Security Subsystem Class: Opal Version 2.02,<br>Revision 1.0 or later, and all mandatory feature sets (e.g., Additional DataStore, Block SID<br>Authentication, and PSID feature sets).|
|TCG-FEATURE-2|TCG devices shall support TCG Single User Mode feature set Version 1.00, Revision 2.00 or<br>later.|
|TCG-FEATURE-3|TCG devices shall support TCG Configurable Namespace Locking (CNL) feature set Version<br>1.02, Revision 1.00 or later with mandatory support for the Namespace Global Range<br>Locking object.  The Namespace Non-Global Range Locking object may be supported.|
|TCG-FEATURE-4|Obsolete, see TCG-FEATURE-1.|
|TCG-FEATURE-5|The current TCG feature set configuration settings, if any, shall persist through a download<br>and activation of firmware code (e.g., TPer Lock State, Single User Mode configuration, no<br>C_PIN Reset).  This is required regardless of the “default setting state” of the new code<br>being downloaded.|
|TCG-FEATURE-6|The device shall support the Data Removal Mechanism Feature Descriptor (Feature Code<br>0404h).  The Data Removal Time Format bit shall be set to 0 to indicate the Data Removal<br>Time value is stored in (value x 2) seconds.  The Data Removal Time shall be less than or<br>equal to 10 seconds perCTO-1.|
|TCG-FEATURE-7|<br>The device shall support at least 5 Additional DataStore Tables, each with a minimum size<br>of 128 KiB.  The capacity of these tables is in addition to the 10 MiB minimum required for<br>the DataStore Table.|

**12.6.2 TCG Communication Layer**

|Requirement ID|Description|
|---|---|
|TCG-COMM-1|The device shall support ComID management, and the Level 0 Discovery TPer Feature<br>Descriptor shall report ComID Mgmt supported.|
|TCG-COMM-2|The device shall support at least 2 Static ComIDs.|
|TCG-COMM-3|The device should support at least 2 Dynamic ComIDs.|
|TCG-COMM-4|MaxComIDTime shall be at least 120 seconds.|
|TCG-COMM-5|MaxComIDTime shall be greater than DefSessionTimeout.|

<!-- page 188 -->
**12.6.3 TCG Session Layer**

|Requirement ID|Description|
|---|---|
|TCG-SES-1|A single Read-Write Session shall be supported per SP and shall be indicated by<br>MaxSessions.  It is not required to support an active RW session on the AdminSP at the<br>same time as sessions on other SPs, because this would violate the TCG Storage<br>Architecture Core Specification.|
|TCG-SES-2|At least 2 Read-Only Sessions shall be supported per SP and shall be indicated by<br>MaxReadSessions.  SET methods and other TCG commands that modify the TCG<br>configuration state shall be rejected during a Read Only session.|
|TCG-SES-3|DefSessionTimeout shall be included in the Properties Method response from the device.|
|TCG-SES-4|The DefSessionTimeout value shall be 90,000 ms.|
|TCG-SES-5|The MaxSessionTimeout value shall be 0.  This value indicates that there is no limit.|
|TCG-SES-6|The MinSessionTimeout value should be 500 ms.|
|TCG-SES-7|The SessionTimeout parameter of the StartSession method call shall be used to configure<br>the session timeout.|
|TCG-SES-8|Support for setting the SPSessionTimeout column of the SPInfo table is recommended.|

**12.6.4 TCG Transactions**

|Requirement ID|Description|
|---|---|
|TCG-TRAN-1|TCG devices shall support TCG Transactions.|
|TCG-TRAN-2|TCG Nested Transactions may be supported.  If TCG Nested Transactions are supported, all<br>supported transactions including any nested transactions shall be reflected in the<br>MaxTransactionLimit property.|

**12.6.5 TCG Authentication**

|Requirement ID|Description|
|---|---|
|TCG-AUTH-1|TCG devices shall enforce a minimum password length (C-PIN PinLength of 16) of 16 bytes<br>for all TCG Opal authorities.|
|TCG-AUTH-2|TCG devices shall allow a password length (C-PIN PinLength of 32) of at least 32 bytes for<br>all TCG Opal authorities.|
|TCG-AUTH-3|TCG devices shall set the default TryLimit to 10 for all TCG Opal authorities. The value of<br>the Tries column shall only be cleared to 0 for the mandatory reasons specified in the TCG<br>Storage Architecture Core Specification (e.g., do not clear the Tries column via the Set<br>method, do clear it upon successful authentication or power cycle).|
|TCG-AUTH-4|Authentication of each C_PIN shall be delayed in order to limit how fast the next<br>authentication of that C_PIN can occur.<br>• <br>The delay shall be at least 100 ms and should not exceed 250 ms and I/O shall not be<br>blocked during this time.<br>• <br>The delay shall apply regardless of whether the authentication is successful.<br>• <br>The device manufacturer shall supply documentation with the implemented delay<br>value.<br>• <br>The time limit should be enforced cryptographically (e.g., by tuning the number of<br>PBKDF iterations to reach the target time).|
|TCG-AUTH-5|The Persistence column shall be set to false for all C_PIN rows.|

<!-- page 189 -->
**12.6.6 TCG Crypto**

|Requirement ID|Description|
|---|---|
|TCG-CRYPTO-1|If TCG Opal SP has been activated and the host has supplied an authority password, the<br>device shall use that password as an added source of randomness for its Deterministic<br>Random Number Generator (DRNG).<br>For example, the device may use KDF (PBKDF2) on the user provided locking range<br>password to generate an output of equal length to the required locking range key length<br>plus DRNG seed length.  This output can then be utilized in parts, one part as Opal locking<br>range key and the other part as an additional input to the DRNG.  If the DRNG<br>implementation does not allow the use of additional input, then an alternative option<br>would be to XOR this output (e.g., from PBKDF2 operation) with initial DRNG seed.|

**12.6.7 TCG Locking Security Provider**

|Requirement ID|Description|
|---|---|
|TCG-LOCKING-1|The number of Locking Ranges supported shall be greater than or equal to the maximum<br>number of NVMe namespaces supported on the device.|
|TCG-LOCKING-2|The LockingSP of the device shall support at least one User per Locking Range.|
|TCG-LOCKING-3|The K_AES_256 Table shall be supported.|
|TCG-LOCKING-4|The K_AES_256 Table’s Key columns shall not be readable by the host or be accessible<br>outside the device in any manner.|
|TCG-LOCKING-5|Any attempt to remove the Power Cycle reset type from a LockOnReset column set value<br>shall be rejected.|
|TCG-LOCKING-6|The LockingSP of the device shall support at least 4 Admins.|

**12.6.8 TCG PSID Feature Set**

|Requirement ID|Description|
|---|---|
|TCG-PSID-1|The PSID shall not be deterministic, shall comprise at least 160 bits of entropy. The<br>entropy shall be unique for each device.<br>The PSID shall not be derived from any information that is available without physical<br>access to the device.<br>For example, the PSID shall not be the same as the MSID, the PSID shall not be derived<br>from the device serial number or the date of manufacture because these can be read via<br>the device interface or obtained from other documentation. The PSID shall not be the<br>serial number of the drive hashed with a secret string shared with any other device or<br>among all devices, because the entropy shall be unique for each device.<br>The presence of the PSID on the device label does not violate this requirement.|
|TCG-PSID-2|The PSID shall consist of 32 ASCII characters. The allowed ASCII characters are upper case<br>letters, lower case letters and the digits 0-9. The characters ‘I’, ‘l’, ‘O’ and ’o’ (i.e., 49h,<br>6Ch, 4Fh and 6Fh) and the digits ‘0’ and ‘1’ (i.e., 30h and 31h) shall not be used to limit<br>possible visual confusion.|
|TCG-PSID-3|The generation method for the PSID shall be documented and provided to the customer.|

<!-- page 190 -->
|Requirement ID|Description|
|---|---|
|TCG-PSID-4|After the PSID is provisioned in manufacturing, the PSID shall not be persistently stored in<br>a form that makes retrieval or reconstruction of the PSID by firmware possible, either on<br>the drive or outside the drive (e.g., it is acceptable to store the PSID on the drive hashed<br>via a cryptographic hash or KDF such that the hashed PSID can only be used to verify a PSID<br>input from the host).<br>The presence of the PSID on the device label does not violate this requirement.|
|TCG-PSID-5|Once manufacturing is complete, the PSID shall not be stored anywhere other than on the<br>physical drive label.|

## **13 Device Profiles**

The following are device profiles. This section is intended to be firmware-based configuration settings
configured by device suppliers when manufacturing a device. A device may be configured with a mix of A
and/or B settings. Each customer shall provide their A/B preference for each configuration setting.

The following conventions are used for the Device Profile Table:

|Convention|Definition|
|---|---|
|R|Required.  This shall be supported.|
|O|Optional.  This may be supported.|
|P|Prohibited.  This shall not be supported.|

|Requirement<br>ID|Description|Configuration Setting|Col4|
|---|---|---|---|
|**Requirement**<br>**ID**|**Description**|**A **|**B **|
|DP-CFG-1|Factory Default Sector Size.|4096-byte|512-byte|
|DP-CFG-2|Number of Namespaces Supported.|NSM-4 (16<br>Namespaces)|NSM-5 (16<br>Namespaces per<br>TB)|
|DP-CFG-3|Retention Time based onRETC-1.|1 Month|3 Months|
|DP-CFG-4|NVMe Basic Management Command Supported.|R|P|
|DP-CFG-5|Max M.2 top side height.|2.0 mm|3.2 mm|
|DP-CFG-6|EOL/PLP Failure Mode (Feature Identifier C2h).|Enabled|Disabled|
|DP-CFG-7|Write Uncorrectable command support.|O|R|
|DP-CFG-8|Time-to-Identify-Ready based on TTR-1.|<= 1 second|<= 10 seconds<br>after a normal<br>shutdown<br><= 60 seconds<br>after an abrupt<br>shutdown|
|DP-CFG-9|Time-to-I/O-Ready based onTTR-2 andTTR-22.|<= 20 seconds|<= 10 seconds<br>after a normal<br>shutdown<br><= 60 seconds<br>after an abrupt<br>shutdown|

<!-- page 191 -->
|Requirement<br>ID|Description|Configuration Setting|Col4|
|---|---|---|---|
|**Requirement**<br>**ID**|**Description**|**A **|**B **|
|DP-CFG-10|In addition to the requirements inTTR-4, the<br>device shall keep CSTS.RDY = 0 until the device is<br>able to service I/O commands and Admin<br>commands that require media access<br>successfully.|P1|R|
|DP-CFG-11|Support for the Lockdown command on the in-<br>band interface. If the Lockdown command is<br>prohibited, then the Lockdown command shall<br>not be supported in-band (e.g., bit 10 of the<br>Optional Admin Command Support field in the<br>Identify Controller data structure shall be cleared<br>to 0b).|R|P|
|Notes:<br>1. This requirement overrides the NVM Express Base Specification requirement to operate in Controller<br>Ready With Media Mode when CAP.CRMS.CRIMS is cleared to 0b as required byNVMe-CFG-20.|Notes:<br>1. This requirement overrides the NVM Express Base Specification requirement to operate in Controller<br>Ready With Media Mode when CAP.CRMS.CRIMS is cleared to 0b as required byNVMe-CFG-20.|Notes:<br>1. This requirement overrides the NVM Express Base Specification requirement to operate in Controller<br>Ready With Media Mode when CAP.CRMS.CRIMS is cleared to 0b as required byNVMe-CFG-20.|Notes:<br>1. This requirement overrides the NVM Express Base Specification requirement to operate in Controller<br>Ready With Media Mode when CAP.CRMS.CRIMS is cleared to 0b as required byNVMe-CFG-20.|

## **14 Labeling**

The following sample label is meant to be used to refer to the label requirements in Section 14.1 – Label
Requirements. It is not a model label and any markings on it are informative only. See the specifics in
Section 14.1 – Label Requirements for actual requirements:

<!-- page 192 -->
### **14.1 Label Requirements**

|Item|Format|Text<br>Required|Barcode<br>Required|Barcode<br>Type|
|---|---|---|---|---|
|Barcode-1|‘Model Number’<br>‘Underscore’ ‘Serial Number’<br>\n.|No|Yes|2d|
|Model Number|See LABL-11 (Model Number<br>shall match).|Yes|No|N/A|
|Serial Number|See LABL-12 (Serial Number<br>shall match), LABL-15<br>(certification logos), and<br>LABL-17 (Serial Number<br>format).|Yes|No|N/A|
|Manufacturer’s<br>Part Number|Number used for ordering.|Yes, if<br>different<br>from Model<br>Number|No|N/A|
|Capacity|Number of GB or TB.|Yes|No|N/A|
|STORAGE DEVICE|Text shall be “STORAGE<br>DEVICE”.|Yes|No|N/A|
|PSID|TCG Storage Security<br> Subsystem Class: Opal<br>Specification|Yes|No|N/A|
|Barcode-2|‘PSID’ \n|No|Yes|2d|
|HW Revision||Yes|No|N/A|
|Firmware Name<br>& Revision||No|No|N/A|
|Regulatory Mark|See LABL-15 (certification logos).|See LABL-15 (certification logos).|No|N/A|
|Country<br>Certification<br>Numbers|See LABL-15 (certification logos).|See LABL-15 (certification logos).|No|N/A|
|Certification<br>Logos|See LABL-15 (certification logos).|See LABL-15 (certification logos).|No|N/A|
|RoHS/<br>Green|See LABL-15 (certification logos).|See LABL-15 (certification logos).|No|N/A|

|Requirement ID|Description|
|---|---|
|LABL-1|The following fields are required information that shall be placed on the label:<br>**Item**<br>**Format**<br>**Text**<br>**Required**<br>**Barcode**<br>**Required**<br>**Barcode**<br>**Type**<br>Barcode-1<br>‘Model Number’<br>‘Underscore’ ‘Serial Number’<br>\n.<br>No<br>Yes<br>2d<br>Model Number<br>See LABL-11 (Model Number<br>shall match).<br>Yes<br>No<br>N/A<br>Serial Number<br>See LABL-12 (Serial Number<br>shall match), LABL-15<br>(certification logos), and<br>LABL-17 (Serial Number<br>format).<br>Yes<br>No<br>N/A<br>Manufacturer’s<br>Part Number<br>Number used for ordering.<br>Yes, if<br>different<br>from Model<br>Number<br>No<br>N/A<br>Capacity<br>Number of GB or TB.<br>Yes<br>No<br>N/A<br>STORAGE DEVICEText shall be “STORAGE<br>DEVICE”.<br>Yes<br>No<br>N/A<br>PSID<br>TCG Storage Security<br> Subsystem Class: Opal<br>Specification<br>Yes<br>No<br>N/A<br>Barcode-2<br>‘PSID’ \n<br>No<br>Yes<br>2d<br>HW Revision<br> <br>Yes<br>No<br>N/A<br>Firmware Name<br>& Revision<br> <br>No<br>No<br>N/A<br>Regulatory Mark<br>See LABL-15 (certification logos).<br>No<br>N/A<br>Country<br>Certification<br>Numbers<br>See LABL-15 (certification logos).<br>No<br>N/A<br>Certification<br>Logos<br>See LABL-15 (certification logos).<br>No<br>N/A<br>RoHS/<br>Green<br>See LABL-15 (certification logos).<br>No<br>N/A|
|LABL-2|The Model Number on the shipping label shall match the Model Number used during<br>qualification.|
|LABL-3|The minimum font size shall be 3 points, and the typical size should be 6 points.|
|LABL-4|For the Capacity field, if there are space constraints, the manufacturer may remove<br>“Capacity:” and just show “960GB” or “60TB” for example.|

<!-- page 193 -->
|Requirement ID|Description|
|---|---|
|LABL-5|To distinguish Model Number and Serial Number, Barcode-1 shall have an underscore “_”<br>between the Model Number portion and the Serial Number portion.<br>Example:<br>Model Number: DSSD-Example-Model-Number<br>Serial Number: 0923Zjx8UqN9UxX92LHN<br>Barcod-1 Readout: DSSD-Example-Model-Number_0923Zjx8UqN9UxX92LHN|
|LABL-6|There shall be a line with the text “STORAGE DEVICE”.|
|LABL-7|The following fields are optional information that can be placed on the label at the<br>discretion of the device maker.  Placement is also at the device makers’ discretion if such<br>information does not interfere with the mandatory information above.  No additional<br>barcode shall be present.<br>**Item**<br>**Format**<br>**Text**<br>**Required**<br>**Barcode**<br>**Required**<br>**Barcode**<br>**Type**<br>Processor<br>Code (BA)<br> <br>Optional<br>No<br>N/A<br>Maker Logo<br> <br>Optional<br>No<br>N/A<br>Rated Voltage<br>& Current<br> <br>Optional<br>No<br>N/A<br>Production Date<br>DDMMYYYY: DD (Date), MM<br>(Month), YYYY (Year)<br>Optional<br>No<br>N/A<br>Weekly Code<br>YYWW: YY (Year), WW (Week)<br>Optional<br>No<br>N/A<br>Warranty VOID<br>IF REMOVED<br> <br>Optional<br>No<br>N/A<br>Makers Own<br>Label Material<br>Number<br> <br>Optional<br>No<br>N/A<br>Website,<br>Company<br>Address<br> <br>Optional<br>No<br>N/A<br>SSD<br> <br>Optional<br>No<br>N/A<br>Product Series<br>Name<br> <br>Optional<br>No<br>N/A<br>SA: Value used<br>within<br>manufacturing<br> <br>Optional<br>No<br>N/A<br>PBA: Physical<br>Board Address<br>(identifies the<br>physical<br>configuration of<br>the device)<br> <br>Optional<br>No<br>N/A|

|Item|Format|Text<br>Required|Barcode<br>Required|Barcode<br>Type|
|---|---|---|---|---|
|Processor<br>Code (BA)||Optional|No|N/A|
|Maker Logo||Optional|No|N/A|
|Rated Voltage<br>& Current||Optional|No|N/A|
|Production Date|DDMMYYYY: DD (Date), MM<br>(Month), YYYY (Year)|Optional|No|N/A|
|Weekly Code|YYWW: YY (Year), WW (Week)|Optional|No|N/A|
|Warranty VOID<br>IF REMOVED||Optional|No|N/A|
|Makers Own<br>Label Material<br>Number||Optional|No|N/A|
|Website,<br>Company<br>Address||Optional|No|N/A|
|SSD||Optional|No|N/A|
|Product Series<br>Name||Optional|No|N/A|
|SA: Value used<br>within<br>manufacturing||Optional|No|N/A|
|PBA: Physical<br>Board Address<br>(identifies the<br>physical<br>configuration of<br>the device)||Optional|No|N/A|

<!-- page 194 -->
|Requirement ID|Description|Col3|Col4|Col5|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||WWN: World<br>Wide Number<br>(unique for each<br>device)||Optional|No|N/A||
|LABL-8|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|To ensure that datacenter operations personnel can quickly and easily identify devices that<br>have been ticketed for field replacement, it is mandatory to have the proper identifying<br>fields on the label(s), in the format specified in this table.|
|LABL-9|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|The label shall not degrade over the standard SSD lifetime under standard operating<br>conditions.|
|LABL-10|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|For each form factor, the label shall be placed as follows:<br>• <br>M.2: the label shall be placed on the top side of the device as defined in the PCI-SIG<br>M.2 form factor specification.<br>• <br>E1.S: the label shall be placed on the Primary side of the device as defined in the<br>SFF-TA-1006 form factor specification.<br>• <br>E1.L: the label shall be placed on either the Primary or Secondary side of the device as<br>defined in the SFF-TA-1007 form factor specification.<br>• <br>E3: the primary label shall contain the drive information (e.g., model number, serial<br>number, manufacturing info, firmware revision) and be placed on the top label area as<br>defined in the SFF-TA-1008 form factor specification.  If more space is needed a label<br>may also be placed on the bottom label area with regulatory marks.|
|LABL-11|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|The Model Number in Barcode-1, the Model Number printed on the label and the Model<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 63:24) shall all<br>match unless exempted in writing by the customer.|
|LABL-12|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|The Serial Number in Barcode-1, the Serial Number printed on the label and the Serial<br>Number returned in Identify Controller Data Structure (CNS 01h, byte offset 23:04) shall all<br>match.|
|LABL-13|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|This Hardware Revision printed on the label and returned by the nvme-cli utility shall<br>match.|
|LABL-14|All other electronically readable information shall also match their counterparts printed on<br>the label.|All other electronically readable information shall also match their counterparts printed on<br>the label.|All other electronically readable information shall also match their counterparts printed on<br>the label.|All other electronically readable information shall also match their counterparts printed on<br>the label.|All other electronically readable information shall also match their counterparts printed on<br>the label.|All other electronically readable information shall also match their counterparts printed on<br>the label.|All other electronically readable information shall also match their counterparts printed on<br>the label.|
|LABL-15|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|The following certification logos and their corresponding certifications are required:<br>**Regulatory**<br>**Mark/Text**<br>**Description**<br>Regulatory Model<br>Number<br>Unique regulatory Identifier.<br>Made in<br>Country of Origin.<br>Manufacturer or<br>Brand name<br>Identification of the responsible party for placing the device into<br>the market.<br>Address of the<br>Manufacturer<br>Required for devices with the CE mark or UKCA mark.<br>Date of<br>Manufacture<br>Not needed if embedded in the Serial Number.|

|Regulatory<br>Mark/Text|Description|
|---|---|
|Regulatory Model<br>Number|Unique regulatory Identifier.|
|Made in|Country of Origin.|
|Manufacturer or<br>Brand name|Identification of the responsible party for placing the device into<br>the market.|
|Address of the<br>Manufacturer|Required for devices with the CE mark or UKCA mark.|
|Date of<br>Manufacture|Not needed if embedded in the Serial Number.|

<!-- page 195 -->
|Requirement ID|Description|Col3|Col4|Col5|
|---|---|---|---|---|
|||Serial Number|Alpha-Numeric, 12-20 digits with the first 4 digits indicating:<br>Date of Manufacturing in Work Week and Year<br>WWYY1234567890123456.||
||||[Europe] Compliance with EU WEEE directive 2010/19/EU.|[Europe] Compliance with EU WEEE directive 2010/19/EU.|
||||[Europe] Compliance with EU EMC directive 2014/30/EU and RoHS<br>directive 2011/65/EU.|[Europe] Compliance with EU EMC directive 2014/30/EU and RoHS<br>directive 2011/65/EU.|
|||<br>|[Australia, New Zealand] Compliance with requirements of the<br>relevant Australian ACMA Standards, under the<br>Radiocommunications Act 1992 and the Telecommunications Act<br>1997.|[Australia, New Zealand] Compliance with requirements of the<br>relevant Australian ACMA Standards, under the<br>Radiocommunications Act 1992 and the Telecommunications Act<br>1997.|
||||[Japan] Compliance with Japan VCCI requirements.|[Japan] Compliance with Japan VCCI requirements.|
|||<br>XXXX-XX-XX|[Korea] Compliance with requirements of the Radio Research<br>Laboratory Ministry of Information and Communication Republic of<br>Korea.|[Korea] Compliance with requirements of the Radio Research<br>Laboratory Ministry of Information and Communication Republic of<br>Korea.|
|||CAN ICES-<br>3(*)/NMB-3(*)|[Canada] Compliance with Canada standard ICES 003. Where * is<br>either A or B.|[Canada] Compliance with Canada standard ICES 003. Where * is<br>either A or B.|
||||[USA] Optional. Compliance with United States Federal<br>Communications Commission requirements.|[USA] Optional. Compliance with United States Federal<br>Communications Commission requirements.|
||||[USA] Compliance with UL standards and Canadian Safety<br>Standards.|[USA] Compliance with UL standards and Canadian Safety<br>Standards.|
||||[Taiwan] Compliance with Taiwan EMC and RoHS.|[Taiwan] Compliance with Taiwan EMC and RoHS.|
||||[China] Compliance with Chinese environmental requirements. The<br>number inside the circle is usually 10 or 20.|[China] Compliance with Chinese environmental requirements. The<br>number inside the circle is usually 10 or 20.|
||||[Morocco] Compliance with Moroccan EMC standards.|[Morocco] Compliance with Moroccan EMC standards.|
||||[United Kingdom] Compliance with United Kingdom standards.<br>Mandatory after 1/1/2022. Guidance to UKCA marking.|[United Kingdom] Compliance with United Kingdom standards.<br>Mandatory after 1/1/2022. Guidance to UKCA marking.|
|LABL-16|If the surface of any component or casing will reach a temperature of 70°C (158°F) or <br>greater the following warning logo shall be either printed on the label or placed separately<br>on the device:<br> <br>In addition, instructional safeguards shall be provided in accordance with IEC 62368-1 3rd <br>Edition or later.|If the surface of any component or casing will reach a temperature of 70°C (158°F) or <br>greater the following warning logo shall be either printed on the label or placed separately<br>on the device:<br> <br>In addition, instructional safeguards shall be provided in accordance with IEC 62368-1 3rd <br>Edition or later.|If the surface of any component or casing will reach a temperature of 70°C (158°F) or <br>greater the following warning logo shall be either printed on the label or placed separately<br>on the device:<br> <br>In addition, instructional safeguards shall be provided in accordance with IEC 62368-1 3rd <br>Edition or later.|If the surface of any component or casing will reach a temperature of 70°C (158°F) or <br>greater the following warning logo shall be either printed on the label or placed separately<br>on the device:<br> <br>In addition, instructional safeguards shall be provided in accordance with IEC 62368-1 3rd <br>Edition or later.|
|LABL-17|The format of the Serial Number shall have no leading spaces (e.g., 1234567890123456).|The format of the Serial Number shall have no leading spaces (e.g., 1234567890123456).|The format of the Serial Number shall have no leading spaces (e.g., 1234567890123456).|The format of the Serial Number shall have no leading spaces (e.g., 1234567890123456).|

<!-- page 196 -->
|Requirement ID|Description|
|---|---|
|LABL-18|The Model Number shall have no leading spaces.|
|LABL-19|Barcodes shall be printed using Datamatrix ECC200 or Model 2 QR code only.|
|LABL-20|QR codes shall use a minimum of ECC Level M (15%).|
|LABL-21|The density of the barcode shall be 10 mil or larger.|
|LABL-22|The label shall only be printed on Polyester or Plastic labels using a Wax/Resin ribbon.|
|LABL-23|The PSID shall be printed on the label in its direct 32-character alphanumeric<br>representation without any ancillary delimiting characters (e.g., underscore, dash,<br>backslash, forward slash, etc.) and shall exactly match the readout of Barcode-2 (see the<br>label example at the top of this section).|

## **15 Compliance**

### **15.1 ROHS Compliance**

|Requirement ID|Description|
|---|---|
|ROHS-1|The Supplier shall provide component-level reporting on the use of listed materials by<br>concentration (ppm) for all homogenous materials.|

### **15.2 ESD Compliance**

|Requirement ID|Description|
|---|---|
|ESD-1|Device manufacturer shall provide ESD immunity level (HBM - Human Body Model)<br>measured in accordance with IEC-61000-4-2.|

### **15.3 EMC Compliance**

|Requirement ID|Description|
|---|---|
|EMC-1|The device shall comply with the requirements of FCC / EN55032 Class B Radiated<br>Emissions.|

## **16 Shock and Vibration**

The shock and vibration specifications for storage devices are in the following table:

|Requirement ID|Description|
|---|---|
|SV-1|The non-operational shock requirement is 700G, half-sine, 0.5 ms, total 6 shocks, along all<br>three axes (+/-).|
|SV-2|The vibration requirement during operation is: 1.8Grms, 5-500-5 Hz, Random Vibe, 20 min<br>along all three axes.|
|SV-3|The vibration requirement during non-operation is: 3.13Grms, 5-800-5 Hz, total 6 sweeps<br>along all three axes, 20 minutes per sweep.|

<!-- page 197 -->
|Requirement ID|Description|
|---|---|
|SV-4|Validation flow for Shock and Vibration:<br>1. UUT (Unit Under Test), test fixture should be visually inspected and ensured that<br>everything is torqued or secured as needed.  Pictures of test fixture with and w/o UUT<br>should be provided.<br>2. Baseline performance of device should be gathered and used as a reference against<br>post S&V data to ensure no performance impact incurred.<br>3. Once S&V testing is completed, repeat visual inspection to the UUT and test fixture to<br>ensure no physical damage or performance impact has occurred to the UUT or test<br>fixture.<br>4. Re-run stress test on the UUT in case of non-op test and provide data indicating no<br>performance impact incurred to the unit.|

## **17 Sustainability Requirements**

The following are the sustainability requirements for devices.

|Requirement ID|Description|
|---|---|
|SUS-1|A Life Cycle Assessment (LCA) aligned with ISO 14040 for the device shall be provided to<br>the customer.|
|SUS-2|Recycled content information per material type shall be provided to the customer.|

## **18 Linux NVMe-CLI Plug-In Requirements**

### **18.1 NVMe-CLI Management Utility**

[The nvme-cli utility (https://github.com/linux-nvme/nvme-cli/tree/master/plugins/ocp) shall be used as](https://github.com/linux-nvme/nvme-cli/tree/master/plugins/ocp)
one of the management utilities for NVMe devices.

|Requirement ID|Description|
|---|---|
|UTIL-1|The SSD supplier must test their SSDs with this utility and ensure compatibility with their<br>device and functionality supported by nvme-cli (e.g., Format, Secure Erase, Firmware<br>Update, etc.).|

### **18.2 NVMe-CLI Plugin Requirements**

|Requirement ID|Description|
|---|---|
|UTIL-PI-1<br>through<br>UTIL-PI-7|Obsolete.  SeeSection 18.1 NVMe-CLI Management Utility.|

<!-- page 198 -->
**18.2.1 NVMe-CLI Plug-In Nomenclature/Functional Requirements**

|Requirement ID|Description|
|---|---|
|UTIL-NM-1<br>through<br>UTIL-NM-10|Obsolete.  SeeSection 18.1 NVMe-CLI Management Utility.|

**18.2.2 NVMe-CLI Plug-In FW Activation History Requirements**

|Requirement ID|Description|
|---|---|
|UTIL-FWHST-1<br>Through<br>UTIL-FWHST-15|Obsolete. SeeSection 18.1 NVMe-CLI Management Utility.|

## **19 Revision History**

|Revision|Date|Release Notes|
|---|---|---|
|1.0|03/16/2020|Initial release based on feedback from the industry.|
|1.0a|06/26/2020|Errata.|
|2.0|05/18/2021|Additional major features and requirements including Latency Monitoring, Device<br>Capabilities, Unsupported Requirements, Datacenter SSD Power States, Multiple<br>Namespaces, Sanitize, NVMe-MI, Write Zeroes, Compare, Fused, Write<br>Uncorrectable, Device Profiles, SPDM and additional security requirements, etc.|
|2.5|09/22/2023|Additional major features and requirements including Telemetry Data Area 1 & 2,<br>Hardware Component log, FDP, DIX, security requirements, etc.|
|2.6|09/11/2024|Errata and other updates in most sections.|

## **20 META Specific Items**

The following items apply specifically to devices delivered to META.

### **20.1 Configuration Specifics**

|Requirement ID|Description|
|---|---|
|META-CONF-1|For all form factors, SMBus byte 91 bit 6, Firmware Update Enabled bit shall be set to 1b<br>by default from the factory.|
|META-CONF-2|Devices shall not support Error Injection (Feature Identifier C0h) Set Feature.|
|META-CONF-3|Devices shall not support Error Injection (Feature Identifier C0h) Get Feature.|
|META-CONF-4|Devices shall not support Error Recovery (Log Identifier C1h).|

<!-- page 199 -->
|Form Factor|Capacity|Default Power State Upon Factory Exit|
|---|---|---|
|E1.S 25mm|1 TB|7 (10 W)|
|E1.S 25mm|2 TB|6 (12 W)|
|E1.S 25mm|4 TB|5 (14 W)|
|E1.S 25mm|8 TB|4 (16 W)|
|E1.S 25mm|16 TB|2 (20 W)|
|E1.S 9.5mm|1 TB|8 (8.25 W)|
|E1.S 9.5mm|2 TB|7 (10 W)|

|Power State|Maximum Average<br>Power (MAP)|
|---|---|
|0|35 W|
|1|25 W|
|2|20 W|
|3|18 W|
|4|16 W|
|5|14 W|
|6|12 W|
|7|10 W|
|8|8.25 W|

|Requirement ID|Description|
|---|---|
|META-CONF-5|The default power state shall conform to the following table:<br>**Form Factor**<br>**Capacity**<br>**Default Power State Upon Factory Exit**<br>E1.S 25mm<br>1 TB<br>7 (10 W)<br>2 TB<br>6 (12 W)<br>4 TB<br>5 (14 W)<br>8 TB<br>4 (16 W)<br>16 TB<br>2 (20 W)<br>E1.S 9.5mm<br>1 TB<br>8 (8.25 W)<br>2 TB<br>7 (10 W)|
|META-CONF-6|The power state table on the device shall be the following:<br>Power State<br>Maximum Average<br>Power (MAP)<br>0 <br>35 W<br>1 <br>25 W<br>2 <br>20 W<br>3 <br>18 W<br>4 <br>16 W<br>5 <br>14 W<br>6 <br>12 W<br>7 <br>10 W<br>8 <br>8.25 W|
|META-CONF-7|Devices shall be configured to Configuration Setting A as shown inSection 13 Device<br>Profiles.|
|META-CONF-8|<br>DIX-1 shall be supported.|
|<br>META-CONF-9|<br>FDPSRG-1 toFDPSRG-7 shall be supported with support for 4K, 4K+64 (DIX-1), and 512<br>byte sector sizes.|
|META-CONF-10|ForGROWTM-2 the default end of life behavior shall be 11b.  It shall be noted that EOL is<br>defined inEOL-4, EOL-5 andEOL-6 and is not based on the life curve.|
|META-CONF-11|<br>The PLP Failure Mode (Feature Identifier C2h) shall set the factory default value of the<br>End of Life Behavior to 11b (seeSROWTM-13 for additional information.|

### **20.2 Performance Requirements**

The following numbers are the META performance targets for data storage SSD across all form factors.
They are provided to serve as guidance for SSD Vendors. Performance scripts can be found on GitHub at
_[https://github.com/facebookincubator/FioSynth](https://github.com/facebookincubator/FioSynth)_ . The targets are broken down into the following segments:

|Requirement ID|Description|
|---|---|
|META-PERF-1|FB-FIO Synth Flash Targets (for all capacities).|
|META-PERF-2|fb-FIOSynthFlash TRIM Rate targets.|

<!-- page 200 -->
|Requirement ID|Description|
|---|---|
|META-PERF-3|IO.go benchmark target.|
|META-PERF-4|Fileappend benchmark target.|
|META-PERF-5|Sequential write bandwidth.|
|META-PERF-6|Cache Bench target.|
|META-PERF-7|All targets shall be achieved by using “kyber” as the I/O scheduler.|
|META-PERF-8|Obsolete|
|META-PERF-9|BootBench Target|
|META-PERF-10|All tests shall be executed on Kernel 6.4.3 FBK14 or later versions with support for io_uring<br>engine.|
|META-PERF-11|All performance data shall be provided to Meta based on the following configuration in<br>Figure 1.|

_Figure 1 Performance Test Drive Configuration_

### **20.3 Performance Targets for Data-Drive QOS workloads**

Command: fb-FioSynthFlash -w <workload> -d ALL - f <workload>_results

<!-- page 201 -->
*: MB/s per Server Node

### **20.4 Performance Targets for Boot-Drive QOS workloads**

Command: fb-FioSynthFlash -w <workload> -d ALL - f <workload>_results

<!-- page 202 -->
### **20.5 Trim Rate Targets**

- This test measures raw trim performance with no background I/O

- 64M trim >= 50 GiB/s & <= 10 ms P99 trim latency

- 3GB trim >= 500 GiB/s & <= 10 ms P99 trim latency

- 4K time >= 10K trims/sec & <= 19 ms P99 trim latency

### **20.6 IO.go Benchmark Targets**

- This test measures how long the file system is blocked from writing/overwriting a file while a different
file is deleted.

- Less than 4 file sizes total with latency outliers > 10 ms

- No more than 2 latency outliers per file size

- No single latency outlier above 15 ms

- The IO.go targets will be met with XFS, EXT-4 & BTRFS file systems.

### **20.7 Fileappend Benchmark Targets**

- This test measures how long the file system is blocked from appending to a file while a different file is
deleted.

- No measurable stalls reported by this tool.

- Max acceptable latency outlier is 10 ms when deleting 1 GiB or 2 GiB file.

- Test should be executed for xfs, ext4 and btrfs file systems.

<!-- page 203 -->
### **20.8 Sequential Write Bandwidth**

- Full device (all available user capacity, all namespaces) must be written/filled in 180 minutes or less.

- Simple single-threaded sequential write FIO script to fill device.

### **20.9 CacheBench Targets**

- A benchmarking tool that is a supplement for FB FIO Synth Flash tool on measuring performance for
cache applications. This is different than the “B Cache” workload in FB FIO Synth Flash.

- Two workloads need to be tested:

`o` Graph Cache Leader

`o` Kvcache WC

- The final allocator and throughput stats from the benchmark will be used to see if the targets are met.

- Send SSD latency versus time file to META using one of the following methods:

`o` Send the raw results log file.

`o` Run the “extract_latency.sh script and return the raw results log file, “.tsv” and “.png” files.

- Vendor nvme-cli plugin with “physical NAND bytes written” metric in the SMART / Health Information
Extended (Log Identifier C0h) needs to be working to get the write amplification.

|Workload|Get Rate|Set Rate|Read Latency (us)|Col5|Col6|Col7|Col8|Col9|Write Amp|
|---|---|---|---|---|---|---|---|---|---|
|**Workload**|**Get Rate**|**Set Rate**|**P50**|**P90**|**P99**|**P99.9**|**P99.99**|**Max**|**Max**|
|**Graph Cache Leader**|87,000|16,000|100|300|800|N/A|3,000|12,000|1.3|
|**Kvcache WC**|3,200|1,500|300|700|2,000|9,000|14,000|15,000|1.4|
|**Workload**|**Get Rate**|**Set Rate**|**Write Latency (us)**|**Write Latency (us)**|**Write Latency (us)**|**Write Latency (us)**|**Write Latency (us)**|**Write Latency (us)**|**Write Amp**|
|**Workload**|**Get Rate**|**Set Rate**|**P50**|**P90**|**P99**||**P99.99**|**P100**|**P100**|
|**Graph Cache Leader**|87,000|16,000|30|50|100|N/A|700|8,000|1.3|
|**Kvcahce WC**|3,200|1,500|100|200|400|9,000|7,000|8,000|1.4|

### **20.10 BootBench Target**

This test measures load on a Boot Device in a stacked environment.

- Download the tool from: github.com/liu-song-6/bootbench.

- Execute ./run.py . FIO 3.20 or newer must be installed as a prerequisite.

- Look at the final_result.txt file for output at the end of the run!

|Workload|Read IOPS (sustained)|Overall Result|
|---|---|---|
|BootBench|At least 60K|Pass, without any errors.|

## **21 Microsoft Specific Items**

The following items apply specifically to Microsoft.

<!-- page 204 -->
### **21.1 Configuration Specifics**

|Requirement ID|Description|
|---|---|
|MS-CONF-1|E1.S form factor devices and M.2 form factor devices shall be formatted to 512-byte<br>sectors from the factory.|
|MS-CONF-2|E1.L form factor devices shall be formatted to 4096-byte sectors from the factory.|
|MS-CONF-3|Obsolete.|
|MS-CONF-4|Obsolete.|
|MS-CONF-5|Obsolete.|
|MS-CONF-6|For all devices, SMBus byte 91 bit 6, Firmware Update Enabled bit shall be set to 1b<br>(Firmware Update is Enabled) by default from the factory.|

## **22 Latency Monitoring Feature Set Theory of Operation**

### **22.1 Overview**

Latency outliers are very undesirable in the data center. The goal of this feature is to allow production
monitoring of SSD QOS outliers and to debug outlier issues in production. This feature will allow suppliers
and hyperscale companies to clearly understand if the outliers are caused by the SSD or other components
in the Host system. This feature enables SSD suppliers to effectively debug latency issues efficiently. This
feature will enable predicting when latency outliers are growing and likely to impact hyperscale customers.
This feature enables many use cases involving understanding and debugging latency issues at scale in a
production environment.

### **22.2 Functional Operation**

**22.2.1 Latency Monitoring Feature Description**

Following is the high-level theory of operation describing how the Latency Monitoring feature works. The
latency of an individual command shall be measured from the time a controller fetches the command from
the SQ to the time when controller writes the CQ entry for the SQ entry it fetched.

**22.2.2 Bucket Description Overview**

There are two types of buckets Active Buckets and Static Buckets. Active Buckets are buckets that are
updated in real time. Static Buckets are buckets which are loaded with snapshots from the Active Buckets.
This is a move from the Active Buckets to the Static Buckets, thus the old values in the Static Buckets are
discarded. The Static Buckets allow hyperscale users to sample the Static Buckets over a fixed time period
to gather statistics.

**22.2.3 Active Bucket Description**

The high-level concept is to create 4 real time buckets groups of active latency tracking command counters.
Each bucket will count latency events which exceed a configured latency threshold. A description of each
bucket is in the following figure:

<!-- page 205 -->
Each bucket contains the following:

- Saturating Read Command Counter with an associated Measured Latency and Latency Timestamp.

- Saturating Write Command Counter with an associated Measured Latency and Latency Timestamp.

- Saturating Deallocate/TRIM Command Counter with an associated Measured Latency and Latency
Timestamp.

For clarity, the opcode to Counter mapping is in the following table:

|Bucket Counter|Opcode|Command|
|---|---|---|
|Read Command Counter|02h|Read|
|Write Command Counter|01h|Write|
|Deallocate/TRIM Command Counter|09h with<br>Attribute – Deallocate (AD) = 1|Dataset Management|

In addition to the command counters there is a Measured Latency data structure, and a Latency Timestamp
data structure associated with each command counter. The Measured Latency and Latency Timestamp
have a direct relationship such that both are updated, or neither are updated. The Measured Latency and
Latency Timestamp will be described later in this document.

**22.2.3.1** **Active Command Counter Behavior**

The active command counters count Read commands, Write commands, and Deallocate/TRIM commands
which exceed a configured latency threshold. These active command counters count until the command
counter saturates or the Active Bucket Timer expires. The behavior for each of these events is as follows:

- Active Command Counter Saturation:

<!-- page 206 -->
`o` If the Command Counter saturates, the counter shall maintain the active value and not wrap.

- Active Bucket Timer Expiration:

`o` If the Active Bucket Timer Expires, then the following occurs:

- The Active Bucket Command Counter values and associated information are moved into Static Bucket
Command Counters, the Active Bucket Command Counters are then cleared to zero and re-start
counting.

- The active command counters shall count regardless of how the Active Latency Minimum Window is
configured.

**22.2.3.2** **Active Bucket Thresholds**

There are multiple Active Command Counter Buckets. The configured latency thresholds determine which
Bucket the command counter shall be incremented in. The following figure shows how there are multiple
Buckets and thresholds for each Bucket:

If the Read, Write, Deallocate/TRIM command completion time is below Threshold A then no counter is
incremented. If the threshold is equal or greater than A and less than B, then the corresponding command
counter in Active Bucket 0 increments. If it is equal to or greater than B and less than threshold C, then the
corresponding command counter in Active Bucket 1 increments.  If it is equal to or greater than C and less
than threshold D, then the corresponding command counter in Active Bucket 2 increments. If it is equal to
or greater than threshold D, then the corresponding command counter in Active Bucket 3 increments. By
following this process all latencies greater than threshold A are counted for Read, Write and
Deallocate/TRIM commands. When configuring the Latency Monitor Feature the thresholds shall always
be configured such that Active Threshold A < Active Threshold B < Active Threshold C < Active Threshold
D.

**22.2.3.3** **Active Bucket Timer Behavior**

The Active Bucket Timer times how long the Bucket Command Counters have been counting. When the
Active Bucket Timer is equal to the Active Bucket Timer Threshold then the following operations shall
occur:

<!-- page 207 -->
1. The following data is moved:

a. Active Bucket Counters 0 - 3 are moved to Static Bucket Counters 0 - 3.
b. Active Latency Timestamps are moved to Static Latency Timestamps.
c. Active Measured Latencies are moved to Static Measured Latencies.
d. Active Latency Timestamp Units are moved to Static Latency Timestamp Units.

2. The Active Bucket items shall then be updated as follows:

a. Active Bucket Counters 0 - 3 are cleared to zero.
b. Active Latency Timestamps are set to invalid (FFFF_FFFF_FFFF_FFFFh).
c. Active Measured Latencies are cleared to zero.
d. Active Latency Timestamp Units are cleared to zero.
e. The Active Latency Minimum Window, if it is running, may be reset or continue to count.
f. Active Bucket Timer is cleared to zero and starts the process of counting over.
g. When looking at the data structures in the Latency Monitor (Log Identifier C3h) it should be

noted that the data in item #1 and #2 above is 16-byte aligned, and the data can be moved
simply by doing a data move of the entire data structure.

**22.2.3.4** **Active Latency Timestamp Format**

The format of the Latency Timestamp follows the Timestamp data structure which is defined in the NVM
Express Base Specification. The Latency Timestamp allows an understanding of where a latency excursion
occurred in terms of wall clock time. The Latency Timestamp time reported shall be based on CQ
completion.

If the device receives a Timestamp Set Features (Feature Identifier 0Eh), then the device shall use this
baseline wall clock time plus the time in milliseconds since the Timestamp was set to determine the
Latency Timestamp of the latency event. If the device receives multiple Timestamp Set Features (Feature
Identifier 0Eh) the most recent Timestamp shall be used as the baseline.

If the device does not receive Set Features with a Timestamp, then the Latency Timestamp shall be
generated based on Power on Hours.

If the device receives a Set Features with a Timestamp and then the device is powered off. When the device
is powered on it shall use the most recent Timestamp it received even if this Timestamp was from before
the device was powered off.

The Active Latency Timestamp Units shall be populated when the Latency Timestamp is updated to
indicate if the Latency Timestamp used Timestamp with Power on Hours to generate the Latency
Timestamp or if only Power on Hours were used to generate the Latency Timestamp.

**22.2.3.5** **Active Measured Latency and Active Latency Timestamp Updates**

The Active Measured Latency is the latency measured from fetching the command in the SQ to updating the
CQ. The Active Measured Latency data structure and the Active Latency Timestamp data structure shall be
updated atomically. They shall not update independently. Each Command Counter
(Read/Write/Deallocate) has an Active Measured Latency, and an Active Latency Timestamp structure
associated with it. The Active Latency Configuration is used to configure this feature.

When the Latency Mode in the Active Latency Configuration is cleared to zero then the following behavior
shall be followed:

- The Active Measured Latency and Active Latency Timestamp will be loaded the first time the command
counter associated with it increments.

<!-- page 208 -->
- The Active Measured Latency and Active Latency Timestamp will not be loaded again until the Active
Measured Latency is reset.

If the Latency Mode is set to 0001h in the Active Latency Configuration, then every time the associated
command counter is incremented the Active Measured Latency will report the largest measured latency
based on the associated command counter. The Active Latency Timestamp will report the time when the
largest latency occurred.

The Active Latency Minimum window also affects when the Active Measured Latency and the Active
Latency Timestamp are updated. This is described in the section on Active Latency Minimum Window.

**22.2.3.6** **Active Latency Minimum Window**

This affects both the Active Measured Latency and the Active Latency Timestamp. This defines the
minimum time between updating the Active Measured Latency and the Active Latency Timestamp for a
single Active Bucket/Counter combination. The feature is only used if the Active Latency Mode is set to
0001h.

If the Active Latency Minimum Window timer is running and the Measured Latency and Latency
Timestamp have been updated, then the Latency Timestamp and Active Measured Latency will not be
updated again until the Active Latency Minimum Window timer has expired. Some examples of this are as
follows:

Example 1:
Assume:

- Active Latency Minimum Window of 5 seconds.

- Latency Mode is Configured for Largest Latency.

- Bucket 2 has a threshold range of 40 ms to 400 ms.

|Time in<br>seconds|Read<br>Counter<br>Bucket 2<br>Latency<br>Event|Active<br>Read<br>Counter<br>Bucket 2<br>Value|Actual<br>Latency|Active<br>Measured<br>Latency|Latency Stamp|Comment|
|---|---|---|---|---|---|---|
|0|N|0|-|-|FFFF_FFFF_FFFF_FFFFh|Actual Latency and<br>Active Measured<br>latency are invalid.|
|0.5|Y|1|50 ms|50 ms|0.5 Seconds|First Latency Event.<br>This starts the Active<br>Latency Minimum<br>window. New latency<br>events will not be<br>recorded until the 5<br>second Active<br>Minimum Window<br>expires at 5.5 seconds.|

<!-- page 209 -->
|Time in<br>seconds|Read<br>Counter<br>Bucket 2<br>Latency<br>Event|Active<br>Read<br>Counter<br>Bucket 2<br>Value|Actual<br>Latency|Active<br>Measured<br>Latency|Latency Stamp|Comment|
|---|---|---|---|---|---|---|
|5.25|Y|2|100 ms|50 ms|0.5 Seconds|Measured Latency and<br>Latency Timestamp is<br>not updated due to<br>Minimum Window is<br>not expired; however,<br>the Active Read<br>Counter is updated.|
|6|Y|3|75 ms|75 ms|6 Seconds|Minimum Window is<br>expired and 75ms is<br>greater than the<br>previous number of<br>50ms, so the Active<br>Measured Latency and<br>Latency Timestamp are<br>updated.|

Example 2:
Assume:

- Active Latency Minimum Window of 5 seconds.

- Latency Mode is Configured for First Latency Event.

- Bucket 2 has a threshold range of 40 ms to 400 ms.

|Time in<br>seconds|Read<br>Counter<br>Bucket 2<br>Latency<br>Event|Active Read<br>Counter<br>Bucket 2<br>Value|Actual<br>Latency|Active<br>Measured<br>Latency|Latency<br>Stamp|Comment|
|---|---|---|---|---|---|---|
|0|N|0|-|-|FFFF_FFFF_<br>FFFF_FFFFh|Actual Latency and<br>Active Measured<br>latency are invalid.|
|0.5|Y|1|150 ms|150 ms|0.5 Seconds|First Latency Event.|
|10|Y|2|200 ms|150 ms|0.5 Seconds|Since the device is in<br>First Latency Event<br>mode, no additional<br>events are recorded.|
|15|Y|3|75 ms|150 ms|0.5 Seconds|Since the device is in<br>First Latency Event<br>mode, no additional<br>events are recorded.|

The Active Latency Minimum Window acts as a filter to ensure there are not a large number of events to
update the Active Measured Latency and the Latency Timestamp. Thus, if the queue depth is 128

<!-- page 210 -->
commands deep and there is a latency event, then there are not 128 updates to these data structures.
Rather the first event is recorded, and the rest of the events are filtered out. It should be noted that the
Active Latency Window is not enforced across power cycles. Thus, after a power cycle the Active Latency
Window shall not start until a Bucket Counter is incremented.

**22.2.3.7** **Static Bucket Description**

In addition to the real time buckets there are static buckets. When the Active Bucket Timer reaches its
configured threshold (Active Bucket Timer Threshold) the active real time buckets shall be loaded into the
static buckets and the active real time buckets shall be reset and start counting from 0. The following
figure describes this:

### **22.2 Persistence Across Power Cycles**

When either a safe or unsafe power transition happens the counters and associated Latency Monitoring
Information shall be saved such that they can be restored on the next power up transition and continue
from where the power cycle left off. There are additional details about this in the C.5 Latency Monitoring
Feature - Challenging Event Handling section.

### **22.3 Debug Logs**

The Latency Monitoring Feature can also enable debug logs to trigger. The Debug Log Trigger Enable
configures which counters shall trigger a debug log the first time the Bucket/Counter combination is
incremented. Only a single debug log shall be generated. Once a Latency Monitor debug log is generated,
until the Latency Monitor debug log is discarded another Latency Monitor debug log cannot be generated.
The Latency Monitor debug log shall be discarded using Set Features for the Latency Monitor or by reading
the Latency Monitor Debug Log.

The Set Features for the Latency Monitor has two mechanisms for discarding the Debug Log. One method
discards the debug log and resets the Latency Monitor feature to a new set of configured values based on

<!-- page 211 -->
the fields in Set Features. The other method discards the Debug Log and has no effect on any of the other
features associated with the Latency Monitor Feature. Thus, the Latency Monitor Feature will keep running
undisturbed when the Debug Log is discarded.

When the Latency Monitor debug log trigger event happens, the following data shall be captured: Debug
Log Measured Latency, Debug Log Latency Timestamp, Debug Log Trigger Source, Debug Log Timestamp
Units, Debug Log Pointer as well as internal information required to debug the issue to root cause.

### **22.4 Latency Monitoring Feature - Challenging Event Handling**

**22.4.1 Power Off/On When Latency Monitoring Feature is Enabled**

When powering off, the Active Bucket Information (Counters, Measured Latency, Latency Timestamp,
Active Bucket Timer) may be slightly off due to concerns with flushing data with unsafe power down. The
Active Bucket Information shall maintain coherency compared to itself when flushing data with unsafe
power down. When the device powers back on the Latency Monitoring Feature shall restore the
Active/Static Bucket/Debug Information including loading the Active Bucket Counter. Once the restoration
is complete then the device shall resume the Latency Monitor functionality. The device shall start
capturing latency data within 2 minutes of power on. Thus, commands for the first 2 minutes may not be
monitored. The Active Latency Window is not enforced across power cycles. Thus, after a power cycle the
Active Latency Window shall not start until a Bucket Counter is incremented.

**22.4.2 Power Off/On When Latency Monitoring Feature is Disabled**

The Latency Monitoring Feature disabled/enabled state shall be persistent across power cycles. When the
Latency Monitor Feature is enabled the associated Latency Monitor configuration information in the
Latency Monitor log page shall persist across power cycles.

**22.4.3 Moving Information from Active to Static Buckets**

When moving data from the active buckets to static buckets it can be challenging to track all the
information. The Active counter shall restart counting no longer than 3 seconds from moving data from
Active to Static Counters.

**22.4.4 Firmware Update**

When activating new firmware, if the Latency Monitoring Feature is enabled, the firmware activation shall
reset the Latency Monitoring Feature just as if a Set Features command to enable the feature was received.
The Latency Monitoring Log shall start updating properly within 2 minutes of firmware activation
completing. Thus, there are command latencies which could be missed after initially activating new
firmware.

### **22.5 Configuring Latency Monitoring**

The Set Features command is used to configure this feature. When the Set Features command is used to
configure this feature all the data structures in both the Active and Static Buckets are reset. The debug log
and related debug information is reset based on the Discard Debug Log Field.
