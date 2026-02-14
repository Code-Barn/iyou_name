# GEDCOM Parser Utility

## Overview

The `gedcom_parser.py` utility is the foundational data import module for this family tree application. It handles parsing GEDCOM (GEnealogical Data COMmunication) files - the standard format for exchanging genealogical data between different software applications.

This parser is responsible for reading GEDCOM files, extracting individual records and family relationships, and converting them into structured Python data objects that the rest of the application can work with.

## What is GEDCOM?

GEDCOM is an open specification for exchanging genealogical data between family history software. The format was originally developed by The Church of Jesus Christ of Latter-day Saints and has become an industry standard.

### Key GEDCOM Concepts

- **Records**: GEDCOM files consist of hierarchical records (INDI for individuals, FAM for families, etc.)
- **Tags**: Each line has a level number, a tag, and optional value/pointer
- **XREF IDs**: Cross-reference identifiers (e.g., `@I1@`, `@F1@`) link records together
- **Sub-tags**: Lines indented under a record provide additional details
- **Name Types**: The TYPE sub-tag can specify alternate names (birth, married, aka, nickname)

### Example GEDCOM Structure

```
0 @I1@ INDI
1 NAME John /Smith/
2 GIVN John
2 SURN Smith
1 BIRT
2 DATE 1 JAN 1980
2 PLACE New York, NY
1 FAMS @F1@
```

## File: gedcom_parser.py

### Location
`/apps/parser/utils/gedcom_parser.py`

### Functions

#### 1. `detect_encoding(file_path: str) -> Optional[str]`

Detects the character encoding of a GEDCOM file using the `chardet` library.

- **Purpose**: GEDCOM files can be encoded in various character sets (UTF-8, Latin-1, Windows-1252, etc.)
- **Returns**: Detected encoding string or None if detection fails
- **Note**: Less critical now as `convert_to_utf8` handles encoding internally

#### 2. `parse_gedcom_data(gedcom_content: str) -> Dict`

The main parsing function. This is the workhorse of the module.

**Input**: A string containing the decoded GEDCOM file content

**Output**: Dictionary with three keys:
- `individuals`: Dict[str, PersonData] - All individuals in the file
- `families`: Dict[str, Dict] - Family relationships
- `root_individuals`: List[str] - IDs of individuals without parents

**Processing Steps**:

1. **Encoding & Initialization**
   - Encodes content to UTF-8 bytes
   - Initializes GedcomReader from ged4py library
   - Detects GEDCOM version (5.5 or 7.0) for compatibility

2. **First Pass: Individual Records**
   - Iterates through all INDI records
   - Extracts:
     - **ID**: XREF identifier (e.g., "X1753")
     - **Name**: Given name, surname, full name
       - Handles multiple NAME records with TYPE sub-tags
       - Prioritizes TYPE=BIRTH for surname when present
     - **Events**: Birth, death, christening, burial, etc.
     - **Demographics**: Sex, title, occupation
     - **Family Links**: FAMC (family where individual is child), FAMS (family where individual is spouse)

3. **Second Pass: Family Records**
   - Iterates through all FAM records
   - Establishes relationships:
     - Husband/wife links via HUSB/WIFE tags
     - Parent-child links via CHIL tags
     - Spouse relationships bidirectionally

4. **Third Pass: Relationship Enrichment**
   - Calculates sibling and half-sibling relationships
   - Links children to appropriate spouses
   - Identifies root individuals (those without parents)

**Key Implementation Details**:

- Uses `ged4py` library for GEDCOM parsing (wraps underlying parser)
- Handles both GEDCOM 5.5.1 and GEDCOM 7.0 formats
- Extensive error handling with try-except blocks
- Debug output via print statements (useful for troubleshooting)
- Name extraction handles alternate names via TYPE sub-tags

#### 3. `convert_to_utf8(file_content: bytes) -> str`

Converts file content to UTF-8 string, handling various encoding issues.

**Features**:
- Uses chardet to detect original encoding
- Tries multiple decoding strategies in order:
  1. UTF-8 with replacement
  2. UTF-8 with BOM handling
  3. Latin-1 (handles all byte values)
  4. Windows-1252
- Cleans up common problematic characters (smart quotes, em-dashes, replacement characters)
- Falls back to raw Latin-1 if all else fails

## Data Model: PersonData

The parser produces `PersonData` dataclass instances (defined in `apps/parser/models.py`):

```python
@dataclass
class PersonData:
    id: str
    full_name: str
    given_name: str
    surname: str
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    father: Optional[str] = None      # Father's ID
    mother: Optional[str] = None      # Mother's ID
    spouse: Optional[List[str]] = None
    children: Optional[List[str]] = None
    siblings: Optional[List[str]] = None
    half_siblings: Optional[List[str]] = None
    spouses_children: Optional[Dict[str, List[str]]] = None  # {spouse_id: [child_ids]}
    events: Optional[List[Dict]] = None
    sex: Optional[str] = None
    title: Optional[str] = None
    occupation: Optional[str] = None
```

## Name Handling

The parser handles GEDCOM's complex name structures:

1. **Primary Name**: Extracted from the first NAME record or `record.name` property
2. **Alternate Names**: Additional NAME records with TYPE sub-tags:
   - `TYPE BIRTH` - Birth name (prioritized for surname)
   - `TYPE MARRIED` - Married name
   - `TYPE MAIDEN` - Maiden name
   - `TYPE AKA` / `_AKA` - Also known as
   - `NICK` - Nickname

**Current Implementation**:
- Searches all NAME records for TYPE=BIRTH
- Uses BIRTH surname when found (fixes married names being incorrectly applied)
- Extracts given name (GIVN) and surname (SURN) from sub-tags

## GEDCOM Version Compatibility

The parser detects and handles differences between GEDCOM versions:

- **GEDCOM 5.5.1**: Traditional format, uses TITL for titles, OCCU for occupations
- **GEDCOM 7.0**: Modern format, more robust encoding (UTF-8 default), different tag structures

## Error Handling

The parser includes extensive error handling:
- Encoding detection failures fall back gracefully
- Missing tags don't crash parsing
- Invalid XREF pointers are handled safely
- Individual parsing errors don't stop entire file processing

## Usage in Application

```python
from apps.parser.utils.gedcom_parser import parse_gedcom_data, convert_to_utf8

# Read file and convert encoding
with open('family.ged', 'rb') as f:
    content = convert_to_utf8(f.read())

# Parse the GEDCOM data
family_data = parse_gedcom_data(content)

# Access parsed data
individuals = family_data['individuals']
families = family_data['families']
```

## Debugging Tips

When troubleshooting GEDCOM parsing:

1. Check server console for debug output (prints parsed individuals)
2. Verify file encoding - non-UTF8 files may have character issues
3. Use ged4py's direct API for raw GEDCOM inspection
4. Check for malformed records that might cause parsing issues
5. Verify XREF IDs are properly formatted (@ID@ format)

## Future Improvements

Potential areas for enhancement:

- Support for additional alternate name types
- More comprehensive GEDCOM 7.0 feature support
- Alternative name storage for display (e.g., show married name as alias)
- Media/notes extraction from records
- Source citation parsing
- Better error recovery for malformed files
