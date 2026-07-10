"""
A1 Scope Identifiers
Implements TS 103 988 clause 6.3.1 - Scope identifier definitions

Defines the 10 scope identifier types used to specify the scope of policy
application, including UE-level, group-level, slice-level, and cell-level scopes.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class PlmnId(BaseModel):
    """
    Public Land Mobile Network Identifier
    
    From TS 103 988 6.3.1 - identifies mobile network operator
    """
    
    mcc: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Mobile Country Code (3 digits)",
        title="MCC"
    )
    mnc: str = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Mobile Network Code (2-3 digits)",
        title="MNC"
    )

    @field_validator('mcc', 'mnc')
    @classmethod
    def validate_numeric(cls, v):
        """Ensure numeric format"""
        if not v.isdigit():
            raise ValueError("MCC and MNC must contain only digits")
        return v

    def __str__(self) -> str:
        """String representation: MCC-MNC"""
        return f"{self.mcc}-{self.mnc}"


class UeIdentifier(BaseModel):
    """
    User Equipment Identifier
    
    From TS 103 988 6.3.1-1 - uniquely identifies a UE within PLMN
    """
    
    ue_identifier: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="UE identifier (IMSI, MSISDN, or other unique ID)",
        title="UE Identifier"
    )
    plmn: PlmnId = Field(
        ...,
        description="PLMN where UE is registered",
        title="PLMN"
    )
    identifier_type: Optional[str] = Field(
        None,
        description="Type of identifier (e.g., 'IMSI', 'MSISDN', 'SUPI')",
        title="Identifier Type"
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "ue_identifier": "310150123456789",
                "plmn": {"mcc": "310", "mnc": "150"},
                "identifier_type": "IMSI"
            }
        }


class GroupIdentifier(BaseModel):
    """
    UE Group Identifier
    
    From TS 103 988 6.3.1-2 - identifies a group of UEs
    """
    
    group_identifier: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Group identifier (unique within PLMN)",
        title="Group Identifier"
    )
    group_type: Optional[str] = Field(
        None,
        description="Type of group (e.g., 'SUPI_RANGE', 'NAME_BASED')",
        title="Group Type"
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description of the group",
        title="Description"
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "group_identifier": "enterprise-dept-sales",
                "group_type": "NAME_BASED",
                "description": "Sales department users"
            }
        }


class SliceIdentifier(BaseModel):
    """
    Network Slice Identifier
    
    From TS 103 988 6.3.1-3 - identifies a network slice
    """
    
    sst: int = Field(
        ...,
        ge=0,
        le=255,
        description="Slice Service Type (0-255)",
        title="SST"
    )
    sd: Optional[str] = Field(
        None,
        min_length=1,
        max_length=3,
        description="Slice Differentiator (optional, 1-3 characters)",
        title="SD"
    )
    plmn: Optional[PlmnId] = Field(
        None,
        description="PLMN for roaming scenarios",
        title="PLMN"
    )

    @field_validator('sd')
    @classmethod
    def validate_sd_format(cls, v):
        """Ensure SD follows specification format"""
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("SD must contain alphanumeric characters only")
        return v

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "sst": 1,
                "sd": "001",
                "plmn": None
            }
        }


class QosClassIdentifier(BaseModel):
    """
    QoS Class Identifier
    
    From TS 103 988 6.3.1-4 - identifies QoS class
    """
    
    qci: int = Field(
        ...,
        ge=0,
        le=255,
        description="QoS Class Identifier (0-255)",
        title="QCI"
    )
    arp: Optional[int] = Field(
        None,
        ge=1,
        le=15,
        description="Allocation and Retention Priority (1-15, optional)",
        title="ARP"
    )
    mbrUl: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum Bit Rate - Uplink (bps)",
        title="MBR Uplink"
    )
    mbrDl: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum Bit Rate - Downlink (bps)",
        title="MBR Downlink"
    )
    gbrUl: Optional[float] = Field(
        None,
        ge=0,
        description="Guaranteed Bit Rate - Uplink (bps)",
        title="GBR Uplink"
    )
    gbrDl: Optional[float] = Field(
        None,
        ge=0,
        description="Guaranteed Bit Rate - Downlink (bps)",
        title="GBR Downlink"
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "qci": 5,
                "arp": 8,
                "mbrUl": 1000000,
                "mbrDl": 2000000
            }
        }


class CellIdentifier(BaseModel):
    """
    Cell Identifier
    
    From TS 103 988 6.3.1-5 - identifies a network cell
    """
    
    cell_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Cell identifier (E-UTRAN Cell ID or gNB Cell ID)",
        title="Cell ID"
    )
    plmn: PlmnId = Field(
        ...,
        description="PLMN of the cell",
        title="PLMN"
    )
    cell_type: Optional[str] = Field(
        None,
        description="Cell type (e.g., 'MACRO', 'SMALL_CELL', 'INDOOR')",
        title="Cell Type"
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "cell_id": "12F45600F123401",
                "plmn": {"mcc": "310", "mnc": "150"},
                "cell_type": "MACRO"
            }
        }


class GlobalGnbId(BaseModel):
    """
    Global gNB Identifier
    
    From TS 103 988 6.3.1-6 - globally unique gNB identifier
    """
    
    plmn: PlmnId = Field(
        ...,
        description="PLMN of the gNB",
        title="PLMN"
    )
    gnb_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="gNB identifier (22-32 bit value)",
        title="gNB ID"
    )
    gnb_name: Optional[str] = Field(
        None,
        description="Human-readable gNB name",
        title="gNB Name"
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "plmn": {"mcc": "310", "mnc": "150"},
                "gnb_id": "100000100001",
                "gnb_name": "gNB-Site-A"
            }
        }


class GuAmI(BaseModel):
    """
    Globally Unique AMF Identifier
    
    From TS 103 988 6.3.1-7 - identifies AMF (Access and Mobility Function)
    """
    
    plmn: PlmnId = Field(
        ...,
        description="PLMN of the AMF",
        title="PLMN"
    )
    amf_region_id: int = Field(
        ...,
        ge=0,
        le=255,
        description="AMF region identifier (0-255)",
        title="AMF Region ID"
    )
    amf_set_id: int = Field(
        ...,
        ge=0,
        le=1023,
        description="AMF set identifier (0-1023)",
        title="AMF Set ID"
    )
    amf_pointer: int = Field(
        ...,
        ge=0,
        le=63,
        description="AMF pointer (0-63)",
        title="AMF Pointer"
    )

    def to_string(self) -> str:
        """String representation of GuAmI"""
        return f"{self.plmn}:{self.amf_region_id:02x}{self.amf_set_id:04x}{self.amf_pointer:02x}"

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "plmn": {"mcc": "310", "mnc": "150"},
                "amf_region_id": 1,
                "amf_set_id": 256,
                "amf_pointer": 1
            }
        }


class GuMmeI(BaseModel):
    """
    Globally Unique MME Identifier
    
    From TS 103 988 6.3.1-8 - identifies MME (4G/LTE mobility)
    """
    
    plmn: PlmnId = Field(
        ...,
        description="PLMN of the MME",
        title="PLMN"
    )
    mme_group_id: int = Field(
        ...,
        ge=0,
        le=65535,
        description="MME group identifier (0-65535)",
        title="MME Group ID"
    )
    mme_code: int = Field(
        ...,
        ge=0,
        le=255,
        description="MME code (0-255)",
        title="MME Code"
    )

    def to_string(self) -> str:
        """String representation of GuMmeI"""
        return f"{self.plmn}:{self.mme_group_id:04x}{self.mme_code:02x}"

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "plmn": {"mcc": "310", "mnc": "150"},
                "mme_group_id": 256,
                "mme_code": 1
            }
        }


class TrackingAreaIdentifier(BaseModel):
    """
    Tracking Area Identifier
    
    From TS 103 988 6.3.1-9 - identifies a tracking area for UE location
    """
    
    plmn: PlmnId = Field(
        ...,
        description="PLMN of the tracking area",
        title="PLMN"
    )
    tac: int = Field(
        ...,
        ge=0,
        le=16777215,
        description="Tracking Area Code (0-16777215)",
        title="TAC"
    )

    def to_string(self) -> str:
        """String representation of TAI"""
        return f"{self.plmn}:{self.tac:06x}"

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "plmn": {"mcc": "310", "mnc": "150"},
                "tac": 1
            }
        }


class TaiList(BaseModel):
    """
    List of Tracking Area Identifiers
    
    From TS 103 988 6.3.1-10 - specifies multiple tracking areas
    """
    
    tracking_areas: List[TrackingAreaIdentifier] = Field(
        ...,
        min_items=1,
        description="List of tracking areas",
        title="Tracking Areas"
    )
    all_plmns: bool = Field(
        False,
        description="If True, applies to all PLMNs (wild card)",
        title="All PLMNs"
    )
    tai_list_type: Optional[str] = Field(
        None,
        description="Type of TAI list (e.g., 'EXPLICIT', 'RANGE')",
        title="TAI List Type"
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "tracking_areas": [
                    {
                        "plmn": {"mcc": "310", "mnc": "150"},
                        "tac": 1
                    }
                ],
                "all_plmns": False
            }
        }


class ScopeIdentifierFactory:
    """
    Factory for creating scope identifier objects
    """
    
    @staticmethod
    def create_plmn(mcc: str, mnc: str) -> PlmnId:
        """Create a PLMN identifier"""
        return PlmnId(mcc=mcc, mnc=mnc)
    
    @staticmethod
    def create_ue_scope(
        ue_id: str,
        mcc: str,
        mnc: str,
        id_type: Optional[str] = None
    ) -> UeIdentifier:
        """Create a UE identifier scope"""
        return UeIdentifier(
            ue_identifier=ue_id,
            plmn=PlmnId(mcc=mcc, mnc=mnc),
            identifier_type=id_type
        )
    
    @staticmethod
    def create_group_scope(
        group_id: str,
        group_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> GroupIdentifier:
        """Create a group identifier scope"""
        return GroupIdentifier(
            group_identifier=group_id,
            group_type=group_type,
            description=description
        )
    
    @staticmethod
    def create_slice_scope(
        sst: int,
        sd: Optional[str] = None,
        mcc: Optional[str] = None,
        mnc: Optional[str] = None
    ) -> SliceIdentifier:
        """Create a slice identifier scope"""
        plmn = PlmnId(mcc=mcc, mnc=mnc) if mcc and mnc else None
        return SliceIdentifier(sst=sst, sd=sd, plmn=plmn)
    
    @staticmethod
    def create_qos_scope(
        qci: int,
        arp: Optional[int] = None,
        mbr_ul: Optional[float] = None,
        mbr_dl: Optional[float] = None
    ) -> QosClassIdentifier:
        """Create a QoS class identifier scope"""
        return QosClassIdentifier(
            qci=qci,
            arp=arp,
            mbrUl=mbr_ul,
            mbrDl=mbr_dl
        )
    
    @staticmethod
    def create_cell_scope(
        cell_id: str,
        mcc: str,
        mnc: str,
        cell_type: Optional[str] = None
    ) -> CellIdentifier:
        """Create a cell identifier scope"""
        return CellIdentifier(
            cell_id=cell_id,
            plmn=PlmnId(mcc=mcc, mnc=mnc),
            cell_type=cell_type
        )
    
    @staticmethod
    def create_gnb_scope(
        mcc: str,
        mnc: str,
        gnb_id: str,
        gnb_name: Optional[str] = None
    ) -> GlobalGnbId:
        """Create a gNB identifier scope"""
        return GlobalGnbId(
            plmn=PlmnId(mcc=mcc, mnc=mnc),
            gnb_id=gnb_id,
            gnb_name=gnb_name
        )
    
    @staticmethod
    def create_amf_scope(
        mcc: str,
        mnc: str,
        region_id: int,
        set_id: int,
        pointer: int
    ) -> GuAmI:
        """Create an AMF identifier scope"""
        return GuAmI(
            plmn=PlmnId(mcc=mcc, mnc=mnc),
            amf_region_id=region_id,
            amf_set_id=set_id,
            amf_pointer=pointer
        )
    
    @staticmethod
    def create_mme_scope(
        mcc: str,
        mnc: str,
        group_id: int,
        code: int
    ) -> GuMmeI:
        """Create an MME identifier scope"""
        return GuMmeI(
            plmn=PlmnId(mcc=mcc, mnc=mnc),
            mme_group_id=group_id,
            mme_code=code
        )
    
    @staticmethod
    def create_tai_list_scope(
        tai_list: List[Dict[str, any]],
        all_plmns: bool = False
    ) -> TaiList:
        """Create a TAI list scope"""
        tas = [
            TrackingAreaIdentifier(
                plmn=PlmnId(mcc=ta['plmn']['mcc'], mnc=ta['plmn']['mnc']),
                tac=ta['tac']
            )
            for ta in tai_list
        ]
        return TaiList(tracking_areas=tas, all_plmns=all_plmns)
