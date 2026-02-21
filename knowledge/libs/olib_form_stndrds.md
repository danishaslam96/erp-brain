# Object Library: OLIB_FORM_STNDRDS
**Source:** `OLIB_FORM_STNDRDS_olb.xml`
**Object Count:** 21

## Tab: `WIZMEN_STANDARD`
**Label:** WIZMEN_STANDARD
**Objects:** 1

## Tab: `AUTHORIZATION`
**Label:** AUTHORIZATION
**Objects:** 20

### Program Units
#### `IS_VALID_FOR_EDIT` (Procedure)
```plsql
PROCEDURE IS_VALID_FOR_EDIT IS&#10;BEGIN&#10;		PCKG_AUTHORIZATION.IS_VALID_FOR_EDIT(:PARAMETER.PARM_AUTH_DOC_TYPE_ID,:TEXT_PURCH_INVOICE_ID,:AUTH_STATUS_ID);&#10;END;&#10;&#10;
```

#### `PRO_EN_DIS_AUTH_BUTTON` (Procedure)
```plsql
PROCEDURE PRO_EN_DIS_AUTH_BUTTON IS&#10;BEGIN&#10;  PCKG_AUTHORIZATION.EN_DIS_AUTH_BUTTONS(:AUTHORIZED_YN, :AUTH_ID,:AUTH_STATUS_ID, :PENDING_STATUS_YN, :APPROVED_STATUS_YN, :REJECTED_STATUS_YN);&#10;END;
```

### Items
| Name | Type | Label | Canvas | Column |
|------|------|-------|--------|--------|
| `AUTH_ID` |  |  | `` | `pimt.auth_id` |
| `AUTH_STATUS_ID` |  |  | `` | `PIMT.AUTH_STATUS_ID` |
| `AUTH_STATUS_DESC` | Display Item |  | `CAN_MAIN` | `asmt.description` |
| `AUTHORIZED_YN` |  |  | `` | `pimt.authorized_yn ` |
| `AUTH_STATUS_EDITABLE_YN` |  |  | `` | `NVL(asmt.editable_yn,1)` |
| `PENDING_STATUS_YN` |  |  | `` | `ASMT.pending_status_yn ` |
| `REJECTED_STATUS_YN` |  |  | `` | `ASMT.rejected_status_yn ` |
| `APPROVED_STATUS_YN` |  |  | `` | `ASMT.approved_status_yn ` |
| `PBTN_SEND_FOR_AUTH` | Push Button | Send for &Auth | `CAN_DEMAND` | `` |
| `PBTN_AUTH_TRACK` | Push Button | Auth &Track | `CAN_DEMAND` | `` |
