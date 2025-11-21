# CLAUDE.md - AI Assistant Guide for IstatDataAna

**Last Updated**: 2025-11-21 (Updated after SDMX 2.0 migration)
**Repository**: ISTAT SDMX Python Client
**Purpose**: Comprehensive guide for AI assistants working on this codebase
**API Version**: SDMX-JSON 2.0

---

## 📋 Project Overview

### What This Project Does
This is a Python client library for interfacing with ISTAT's (Italian National Institute of Statistics) SDMX REST API. It provides:

- **Rate-limited API access**: Automatic rate limiting (5 requests/minute)
- **Metadata management**: Full access to dataflows, datastructures, and codelists
- **Multiple output formats**: CSV, JSON, XML support
- **Data analysis utilities**: Advanced analysis tools for time series data
- **Type hints and documentation**: Well-documented, production-ready code

### Target Users
- Data scientists analyzing Italian statistical data
- Researchers working with ISTAT datasets
- Automation engineers building data pipelines
- Testing professionals validating data quality

### Key Constraints
- **Critical**: ISTAT API has strict rate limit of 5 requests/minute per IP
- **Penalty**: Exceeding rate limit results in 1-2 day IP ban
- **Data size**: Some datasets are very large (50+ MB); always use filters
- **API stability**: ISTAT API can be slow or unavailable; implement retries

### ⚡ IMPORTANT: SDMX 2.0 Format

**The ISTAT API uses SDMX-JSON 2.0 format**, not 1.0. Key differences:

1. **JSON Structure**: Uses `names` object for localized strings
   ```json
   {
     "id": "101_1015",
     "name": "Crops",
     "names": {
       "it": "Coltivazioni",
       "en": "Crops"
     }
   }
   ```

2. **Accept Headers**: Simple headers work best
   - Metadata: `Accept: application/json`
   - Data CSV: `Accept: text/csv`
   - ❌ Avoid versioned SDMX headers like `application/vnd.sdmx.structure+json;version=1.0.0`

3. **URL Structure**: Data endpoint format is `data/{dataflow_id}/{key}`
   - Provider ID (IT1) is implicit, not in URL path
   - Example: `data/101_1015/.A...?startPeriod=2023`

---

## 🗂️ Repository Structure

```
IstatDataAna/
├── istat_sdmx_client.py          # Core client library (main module)
├── istat_advanced_analysis.py    # Advanced analysis utilities
├── esempio_completo_analisi.py   # Complete analysis example (Emilia-Romagna)
├── quickstart.py                 # Quick start guide with examples
├── test_setup.py                 # Setup validation and test suite
├── README.md                     # User documentation (Italian)
└── CLAUDE.md                     # This file - AI assistant guide
```

### File Purposes

| File | Purpose | When to Modify |
|------|---------|----------------|
| `istat_sdmx_client.py` | Core API client class | Adding new API endpoints, fixing bugs |
| `istat_advanced_analysis.py` | Data analysis utilities | Adding new analysis methods |
| `esempio_completo_analisi.py` | Reference implementation | Never - this is example code |
| `quickstart.py` | User onboarding | Adding quick start examples |
| `test_setup.py` | Validation suite | Adding new validation tests |
| `README.md` | User documentation | User-facing feature changes |

---

## 🔑 Core Components

### 1. IstatSDMXClient Class
**Location**: `istat_sdmx_client.py:14-271`

**Responsibilities**:
- API communication with ISTAT SDMX REST endpoint
- Automatic rate limiting enforcement
- Request/response handling
- Error management

**Key Methods**:
```python
# Metadata retrieval
get_dataflows()              # List all available datasets
get_datastructure(id)        # Get schema for a dataflow
get_codelist(id)             # Get dimension value codes
get_available_constraints(id) # Get actually available values

# Data retrieval
get_data(dataflow_id, key, start_period, end_period, format)
```

**Rate Limiting Implementation**:
- Uses `time.sleep()` to enforce 12-second minimum between requests
- Tracked via `self.last_request_time`
- **Never bypass or disable** rate limiting without explicit user request

### 2. IstatDataAnalyzer Class
**Location**: `istat_advanced_analysis.py:14-180`

**Responsibilities**:
- Time series download and preparation
- Feature engineering for ML
- Statistical analysis
- Outlier detection
- Regional comparisons

**Key Methods**:
```python
search_dataflows(keyword)            # Search by keyword
download_timeseries(...)             # Download and prepare data
compare_regions(...)                 # Multi-region comparison
calculate_growth_rate(df)            # YoY growth calculation
detect_outliers(df, method)          # IQR or zscore outliers
aggregate_by_period(df, freq)        # Temporal aggregation
```

---

## 🔧 Development Workflow

### When Adding New Features

1. **Check existing patterns**: Review similar functionality first
2. **Respect rate limiting**: All API calls must go through `_make_request()`
3. **Type hints**: Add type hints for all parameters and returns
4. **Docstrings**: Use NumPy-style docstrings
5. **Error handling**: Wrap API calls in try-except with informative errors
6. **Testing**: Update `test_setup.py` if adding core functionality

### When Fixing Bugs

1. **Identify impact**: Is this a rate limiting bug? (Critical!)
2. **Test locally**: Use `test_setup.py --quick` for validation
3. **Check examples**: Ensure `quickstart.py` still works
4. **Update docs**: Modify README.md if user-facing

### When Refactoring

1. **Preserve API**: Public methods must maintain backward compatibility
2. **Internal changes OK**: Private methods (prefixed `_`) can change freely
3. **Performance**: Be mindful of rate limiting when testing changes

---

## 📝 Code Conventions

### Naming Conventions

- **Classes**: PascalCase (`IstatSDMXClient`, `IstatDataAnalyzer`)
- **Methods**: snake_case (`get_dataflows`, `download_timeseries`)
- **Private methods**: Prefix with `_` (`_rate_limit`, `_make_request`)
- **Constants**: UPPER_SNAKE_CASE (`BASE_URL`, `MAX_REQUESTS_PER_MINUTE`)

### Documentation Style

**Docstring Format** (NumPy style):
```python
def method_name(param1: str, param2: int = 5) -> pd.DataFrame:
    """
    Brief description of what the method does

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails

    Examples:
        >>> client.method_name("test", 10)
        DataFrame with results
    """
```

### Error Handling Patterns

```python
# Good - specific errors with context
try:
    response = self._make_request(endpoint, headers)
    data = response.json()
except requests.exceptions.RequestException as e:
    self.logger.error(f"API request failed for {endpoint}: {e}")
    raise
except ValueError as e:
    raise ValueError(f"Invalid dataflow_id {dataflow_id}: {e}")
```

### Logging Guidelines

- **DEBUG**: Detailed rate limiting info, request details
- **INFO**: High-level operations (downloading data, processing)
- **WARNING**: Recoverable issues, API slowness
- **ERROR**: Failed operations, invalid parameters

---

## 🧪 Testing Strategy

### Validation Approach

The project uses `test_setup.py` for validation rather than traditional unit tests.

**Test Categories**:
1. **Imports**: Dependency availability
2. **Client Init**: Instantiation success
3. **Connectivity**: API reachability
4. **Data Download**: Actual data retrieval
5. **Codelist**: Metadata access

**Running Tests**:
```bash
# Full test suite (slow - rate limited)
python test_setup.py

# Quick validation (connectivity only)
python test_setup.py --quick
```

### Testing Best Practices

**When testing changes**:
- Use `--quick` mode to avoid rate limiting
- Test with small datasets (single city, recent years only)
- Never run automated tests in loops (will trigger IP ban)
- Cache dataflows list locally when testing repeatedly

**Example Test-Friendly Queries**:
```python
# Good - small, specific query
df = client.get_data("41_983", key="..082053..",
                     start_period="2020", end_period="2020")

# Bad - huge query, slow, hits rate limit
df = client.get_data("41_983")  # Downloads everything!
```

---

## 🎯 Common Tasks for AI Assistants

### Task 1: Adding New Dataflow Examples

**Steps**:
1. Verify dataflow ID exists: `client.get_dataflows()`
2. Understand structure: `client.get_datastructure(dataflow_id)`
3. Get dimension codes: `client.get_codelist(codelist_id)`
4. Create example in `quickstart.py` or new example file
5. Update README.md with new dataset info

**Template**:
```python
def esempio_nuovo_dataset():
    """
    Esempio: [Dataset name]
    """
    client = IstatSDMXClient(log_level="INFO")

    df = client.get_data(
        dataflow_id="[ID]",
        key="[filter_key]",
        start_period="2020",
        format="csv"
    )

    print(df.head())
    return df
```

### Task 2: Adding Analysis Methods

**When**: User requests new analysis capability (moving averages, forecasting, etc.)

**Steps**:
1. Add method to `IstatDataAnalyzer` class in `istat_advanced_analysis.py`
2. Use pandas/numpy for implementation
3. Include outlier handling (data quality!)
4. Add example usage in docstring
5. Create visualization example if applicable

**Pattern**:
```python
def new_analysis_method(
    self,
    df: pd.DataFrame,
    value_col: str = 'OBS_VALUE',
    **kwargs
) -> pd.DataFrame:
    """
    [Description]

    Args:
        df: Input DataFrame with time series data
        value_col: Column to analyze
        **kwargs: Additional parameters

    Returns:
        DataFrame with analysis results added
    """
    df = df.copy()  # Don't modify original

    # Implementation

    return df
```

### Task 3: Debugging API Issues

**Common Issues**:

1. **503 Service Unavailable**
   - ISTAT API is overloaded or down
   - Solution: Implement exponential backoff retry

2. **414 URI Too Long**
   - Too many filters in query key
   - Solution: Split into multiple queries, combine results

3. **Empty DataFrame**
   - Invalid filter key or no data for period
   - Solution: Check with `get_available_constraints()`

4. **Rate Limit Ban**
   - User exceeded 5 requests/minute
   - Solution: Wait 24-48 hours, verify rate limiting code

**Debug Checklist**:
```python
# 1. Verify dataflow exists
dataflows = client.get_dataflows()
print(dataflows[dataflows['id'] == 'YOUR_ID'])

# 2. Check available values
constraints = client.get_available_constraints('YOUR_ID')

# 3. Test with minimal query
df = client.get_data('YOUR_ID', key="", start_period="2023")

# 4. Check logs
client.logger.setLevel(logging.DEBUG)
```

### Task 4: Performance Optimization

**Key Principles**:
- **Filter aggressively**: Always use key filters and date ranges
- **Cache metadata**: Save dataflows/codelists to pickle files
- **Batch wisely**: Group related queries to minimize API calls
- **Use appropriate formats**: CSV is faster than JSON for large datasets

**Caching Pattern**:
```python
import pickle
from pathlib import Path

# Cache dataflows (valid for ~1 month)
cache_file = Path("dataflows_cache.pkl")
if cache_file.exists():
    dataflows = pd.read_pickle(cache_file)
else:
    dataflows = client.get_dataflows()
    dataflows.to_pickle(cache_file)
```

---

## 📊 API Usage Patterns

### Understanding SDMX Keys

**Key Structure**: `DIM1.DIM2.DIM3.DIM4.DIM5`

**Syntax**:
- `.` = All values for that dimension
- `VALUE` = Specific value
- `VAL1+VAL2` = Multiple values (OR)
- Empty string = No filtering

**Example for Dataflow 101_1015** (Crops):
```
Dimensions vary by dataflow - use get_datastructure() to discover

Examples:
- ".A..."         → Filter for annual data (first dimension)
- ".A+M..."       → Annual OR Monthly (multiple values)
- ""              → No filters (downloads everything - use with caution!)

Note: Always combine with start_period/end_period to limit data volume
```

### Finding Dimension Values

**Process**:
1. Get structure: `client.get_datastructure(dataflow_id)`
2. Identify dimension names from structure
3. For each dimension, get codelist: `client.get_codelist("CL_DIMENSIONNAME")`
4. Alternative: Use `get_available_constraints()` for only existing combinations

**Common Codelists**:
- `CL_FREQ`: Frequency (A=annual, M=monthly, Q=quarterly, B=biannual, D=daily)
- `CL_AREA`: Geographic areas
- Dimension-specific codelists vary by dataflow - explore with `get_datastructure()`

**Important**: SDMX 2.0 returns `names` object with localized strings:
```python
# Codelist response structure
{
  "id": "A",
  "name": "annual",
  "names": {
    "it": "annuale",
    "en": "annual"
  }
}
```

---

## 🚨 Important Context & Gotchas

### Rate Limiting is Non-Negotiable

**NEVER**:
- Bypass rate limiting
- Reduce `REQUEST_INTERVAL` below 12 seconds
- Run loops of API calls without rate limiting
- Suggest users disable rate limiting

**ALWAYS**:
- Use `_make_request()` method for all API calls
- Warn users about rate limit when suggesting batch operations
- Implement caching for repeated queries

### Data Quality Considerations

**Issues to watch for**:
- Missing values (NaN in OBS_VALUE)
- Negative values (should not exist for count data)
- Outliers (spikes due to data entry errors)
- Inconsistent time periods (gaps in series)

**Validation Pattern**:
```python
# Always validate downloaded data
df = client.get_data(...)

# Check for issues
print(f"Missing values: {df['OBS_VALUE'].isna().sum()}")
print(f"Negative values: {(df['OBS_VALUE'] < 0).sum()}")
print(f"Date range: {df['TIME_PERIOD'].min()} to {df['TIME_PERIOD'].max()}")
```

### Language Context

- **Documentation**: README.md and examples are in Italian
- **Code**: All code, comments, and variable names in English
- **User interaction**: Respect user's language preference
- **ISTAT metadata**: Usually bilingual (Italian/English)

### Dependencies

**Required** (no requirements.txt file - document verbally):
```
requests      # HTTP client
pandas        # Data manipulation
matplotlib    # Plotting
seaborn       # Statistical visualization
numpy         # Numerical computing
```

**Installation command**:
```bash
pip install requests pandas matplotlib seaborn numpy
```

**Python version**: ≥ 3.7 (uses type hints, f-strings)

---

## 🔄 Git Workflow

### Branch Strategy

- **Main branch**: Stable, production-ready code
- **Feature branches**: Prefix with `claude/` for AI assistant work
- **Current branch**: `claude/claude-md-mi8yoe1h3o0k234k-01JtMJprdavqS1F753PCic5s`

### Commit Guidelines

**Commit Message Format**:
```
<type>: <description>

[optional body]

Examples:
feat: Add new forecasting method to IstatDataAnalyzer
fix: Correct rate limiting calculation in _make_request
docs: Update README with new dataset examples
refactor: Simplify outlier detection logic
test: Add validation for large dataset queries
```

**Before Committing**:
1. Run `python test_setup.py --quick`
2. Verify examples still work: `python quickstart.py`
3. Check no sensitive data in commits (API keys, cache files)
4. Update README.md if user-facing changes

---

## 📚 Reference Information

### ISTAT API Endpoints

**Current (recommended)**:
- Base URL: `https://esploradati.istat.it/SDMXWS/rest`
- Status: Active, maintained

**Legacy**:
- Base URL: `http://sdmx.istat.it/SDMXWS/rest`
- Status: Still works but deprecated

### Popular Datasets

| ID | Name (IT) | Name (EN) | Use Case |
|----|-----------|-----------|----------|
| 101_1015 | Coltivazioni | Crops | Agriculture production data |
| 115_333 | Produzione industriale | Industrial production | Economic indicators |
| 47_850 | Prezzi al consumo | Consumer prices | Inflation analysis |
| 144_125 | Occupazione | Employment | Labor market |

**Note**: Always test dataflows with `get_available_constraints()` before downloading large datasets.

### External Resources

- [ISTAT Web Services](https://www.istat.it/it/metodi-e-strumenti/web-service-sdmx)
- [SDMX Standard](https://sdmx.org/)
- [API Guide (Community)](https://ondata.github.io/guida-api-istat/)
- [ISTAT Contact](mailto:dcmt-servizi@istat.it)

---

## 🤖 AI Assistant Best Practices

### When Making Changes

1. **Read before writing**: Always read the file before editing
2. **Preserve examples**: Don't break existing example code
3. **Test suggestions**: Validate code works before suggesting
4. **Consider rate limits**: Be cautious with suggestions involving loops
5. **Respect project structure**: Don't reorganize without user request

### Communication Style

- **Be precise**: Provide file paths with line numbers (e.g., `istat_sdmx_client.py:45`)
- **Show examples**: Always include code examples for new features
- **Warn about gotchas**: Proactively mention rate limiting, data size
- **Language neutral**: Support both Italian and English users

### Error Recovery

**If user reports issues**:
1. Ask for error message and traceback
2. Check if rate limit related (most common issue)
3. Verify API connectivity: `python test_setup.py --quick`
4. Review query parameters (especially `key` format)
5. Check ISTAT API status (may be down)

### Code Review Checklist

Before suggesting code changes:
- [ ] Rate limiting preserved
- [ ] Type hints included
- [ ] Docstring complete
- [ ] Error handling present
- [ ] Logging appropriate
- [ ] No hardcoded values
- [ ] Backwards compatible
- [ ] Examples work

---

## 📈 Project Evolution Notes

**Version**: 1.0 (Initial release)
**Created**: November 2025
**Author**: Created for Franco (Testing/QA professional)

**Design Decisions**:
- Chose function-based rate limiting over decorator for clarity
- Used pandas DataFrame as primary return type (familiar to data scientists)
- Separated core client from analysis utilities (separation of concerns)
- Included complete examples to reduce learning curve
- Italian documentation (target audience)

**Recent Changes (2025-11-21)**:
- ✅ **Migrated to SDMX-JSON 2.0**: Updated all JSON parsing to use `names` object
- ✅ **Simplified Accept Headers**: Changed from versioned SDMX headers to simple `application/json` and `text/csv`
- ✅ **Fixed Data Endpoint URL**: Removed provider_id from path (now implicit)
- ✅ **Windows Encoding Fix**: Added UTF-8 console encoding for Unicode support
- ✅ **Updated Documentation**: All examples now use working dataflow 101_1015
- ⚠️ **Deprecated**: `provider_id` parameter in `get_data()` kept for compatibility but unused
- ℹ️ **Known Issue**: Some historical dataflows (e.g., 41_983) may return 404 - investigate endpoint structure

**Future Considerations**:
- Investigate 404 errors on legacy dataflows
- Add JSON format data download tests
- Implement retry logic with exponential backoff
- Add caching layer for metadata queries
- Async support for concurrent queries (respecting rate limits)
- Integration with other Italian statistical databases
- Export to more formats (Excel, Parquet)

---

## 🎓 Quick Reference

### Minimal Working Example
```python
from istat_sdmx_client import IstatSDMXClient

# Initialize
client = IstatSDMXClient()

# Get available datasets
dataflows = client.get_dataflows()
print(f"Found {len(dataflows)} dataflows")

# Download data with temporal filter
df = client.get_data(
    dataflow_id="101_1015",  # Agriculture crops
    start_period="2022",
    end_period="2023",
    format="csv"
)

print(f"Downloaded {len(df)} records")
print(df.head())
```

### Common Commands
```bash
# Setup validation
python test_setup.py --quick

# Run quickstart
python quickstart.py

# Full example pipeline
python esempio_completo_analisi.py

# Interactive mode
python -i -c "from istat_sdmx_client import IstatSDMXClient; client = IstatSDMXClient()"
```

---

**End of CLAUDE.md** - For questions or clarifications, refer to README.md or examine example files.
