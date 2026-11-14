# ⚡ Quick Start Guide

## Run Tests in 3 Steps

### Step 1: Build & Run
```bash
cd /Users/enesoncu/llm-hacker
docker-compose run --rm box-assembly-test pytest -v tests/test_box_assembly.py
```

Expected output:
```
collected 13 items

tests/test_box_assembly.py::TestHingeDetection::test_hinge_detection_completes PASSED
tests/test_box_assembly.py::TestHingeDetection::test_hinge_origin_is_valid PASSED
...
11 passed, 2 failed in 1.49s
```

### Step 2: Get Report Locally
```bash
docker-compose run --rm -v "$(pwd)/test_failures_report:/out" \
  box-assembly-test bash -c "cp -r /app/test_failures/* /out/ 2>/dev/null || true"
```

### Step 3: View in Browser
```bash
cd test_failures_report
python3 -m http.server 8765
# Open: http://localhost:8765/index.html
```

---

## Key Files

| File | Purpose |
|------|---------|
| `tests/test_box_assembly.py` | 13 comprehensive tests |
| `tests/hinge_detector.py` | PyBullet physics engine |
| `tests/visualizer.py` | 3D snapshots + HTML |
| `SYSTEM_V2.md` | Full technical documentation |
| `REDESIGN_COMPLETE.md` | Migration guide & changes |

---

## Understanding Results

### Test Results
- **11 Passed**: Hinge detection, rotation, watertightness OK
- **2 Failed**: Collision at 45° and 90° (design issue)

### What to Check
1. **HTML Report**: `test_failures_report/index.html`
2. **Snapshots**: Shows body (blue) + lid (red) at each angle
3. **Collision Info**: Which angles cause overlap

### Next Steps if Tests Fail
- Adjust CAD: more clearance gap
- Reposition hinge
- Update STL files
- Re-run tests

---

## Docker Commands

```bash
# Run tests
docker-compose run --rm box-assembly-test pytest -v tests/

# Run with output
docker-compose run --rm box-assembly-test pytest -v -s tests/

# Bash shell in container
docker-compose run --rm box-assembly-test bash

# Rebuild image
docker-compose build --no-cache

# Clean up
docker-compose down
docker system prune
```

---

## STL File Format

- **File**: `bottom.stl` (box body)
- **File**: `top.stl` (lid/cap)
- **Format**: Binary or ASCII STL
- **Requirement**: Must be watertight when loaded together (closed assembly)

---

## For New Designs

1. Export CAD as STL:
   - Body → `bottom.stl`
   - Lid → `top.stl`

2. Copy to repo root:
   ```bash
   cp my_body.stl /Users/enesoncu/llm-hacker/bottom.stl
   cp my_lid.stl /Users/enesoncu/llm-hacker/top.stl
   ```

3. Run tests:
   ```bash
   docker-compose run --rm box-assembly-test pytest -v tests/
   ```

4. Check results in HTML report

---

**Status**: ✅ Ready to use!
