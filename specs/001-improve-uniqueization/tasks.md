# Tasks: Улучшение методов уникализации изображений

**Input**: Design documents from `/specs/001-improve-uniqueization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4, US5)
- Include exact file paths

---

## Phase 1: Setup

**Purpose**: Project restructuring from single file to modular architecture

- [ ] T001 Create directory structure: src/, src/handlers/, src/uniqueizers/, src/utils/, tests/, tests/unit/, tests/integration/
- [ ] T002 [P] Create src/__init__.py with package initialization
- [ ] T003 [P] Create src/config.py with BOT_TOKEN and configuration constants
- [ ] T004 [P] Update requirements.txt with new dependencies (numpy, scikit-image for tests)
- [ ] T005 [P] Create tests/__init__.py and tests/conftest.py with pytest fixtures

---

## Phase 2: Foundational (Core Uniqueization Engine)

**Purpose**: Base infrastructure for all uniqueization methods - BLOCKS all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Base Classes and Utilities

- [ ] T006 [P] Create src/uniqueizers/__init__.py with UniqueizationMethod enum (METADATA, MICRO, LSB, COMBINED)
- [ ] T007 [P] Create src/uniqueizers/base.py with abstract BaseUniqueizer class (process method, quality validation)
- [ ] T008 [P] Create src/utils/__init__.py with utility exports
- [ ] T009 [P] Create src/utils/image.py with image loading, saving, format detection, SSIM calculation wrapper
- [ ] T010 [P] Create src/utils/metadata.py with EXIF/IPTC/XMP removal and random metadata generation

### Uniqueization Methods Implementation

- [ ] T011 [P] Implement MetadataUniqueizer in src/uniqueizers/metadata.py (FR-016, FR-017, FR-018)
- [ ] T012 [P] Implement MicroUniqueizer in src/uniqueizers/micro.py (subpixel shift, brightness/color micro-adjust)
- [ ] T013 [P] Implement LSBUniqueizer in src/uniqueizers/lsb.py (least significant bit modification with numpy)
- [ ] T014 Implement CombinedUniqueizer in src/uniqueizers/combined.py (chains all methods, depends on T011-T013)

### Quality Assurance (US2 - Quality Preservation)

- [ ] T015 Add SSIM validation (>= 0.99) to BaseUniqueizer.validate_quality() in src/uniqueizers/base.py
- [ ] T016 Add size ratio check (<= 1.2) to BaseUniqueizer.validate_quality() in src/uniqueizers/base.py
- [ ] T017 Add PNG transparency preservation in src/utils/image.py
- [ ] T018 Add ICC color profile preservation in src/utils/image.py

**Checkpoint**: All uniqueization methods work standalone with quality guarantees

---

## Phase 3: User Story 1 - Выбор метода уникализации (P1) 🎯 MVP

**Goal**: User sends image → selects method via inline buttons → receives uniqueized image

**Independent Test**: Send image to bot, select any method, verify result has different hash and SSIM >= 0.99

### Handlers Setup

- [ ] T019 [P] [US1] Create src/handlers/__init__.py with handler exports
- [ ] T020 [P] [US1] Create src/handlers/callbacks.py with method selection callback handler (method:metadata, method:micro, method:lsb, method:combined)

### Photo Processing

- [ ] T021 [US1] Create src/handlers/photo.py with photo/document message handler
- [ ] T022 [US1] Implement get_method_keyboard() in src/handlers/callbacks.py returning InlineKeyboardMarkup
- [ ] T023 [US1] Implement process_with_method() in src/handlers/photo.py (downloads image, applies selected uniqueizer, sends result)
- [ ] T024 [US1] Add 30-second timeout with default COMBINED method in src/handlers/photo.py

### Bot Integration

- [ ] T025 [US1] Create src/bot.py with Application setup, command handlers (/start, /help), message handlers
- [ ] T026 [US1] Register photo handler for filters.PHOTO in src/bot.py
- [ ] T027 [US1] Register document handler for filters.Document.IMAGE in src/bot.py
- [ ] T028 [US1] Register callback query handler for method selection in src/bot.py

### Error Handling

- [ ] T029 [US1] Add error handling for unsupported formats (not JPEG/PNG) in src/handlers/photo.py
- [ ] T030 [US1] Add error handling for file too large (> 20MB) in src/handlers/photo.py
- [ ] T031 [US1] Add error handling for corrupted images in src/handlers/photo.py

**Checkpoint**: Bot accepts image, shows method buttons, processes with selected method, returns uniqueized file

---

## Phase 4: User Story 3 - Генерация нескольких копий (P1)

**Goal**: User selects copy count (1-100) → receives single file or ZIP archive

**Independent Test**: Send image, select method, select count > 1, verify ZIP contains correct number of unique files

### Archive Utility

- [ ] T032 [P] [US3] Create src/utils/archive.py with create_zip_archive(images: List[Tuple[bytes, str]]) -> BytesIO

### Copy Count Selection

- [ ] T033 [US3] Add get_count_keyboard() in src/handlers/callbacks.py returning InlineKeyboardMarkup with [1, 5, 10, 20, Custom]
- [ ] T034 [US3] Add count selection callback handler (count:1, count:5, count:10, count:20, count:custom) in src/handlers/callbacks.py
- [ ] T035 [US3] Add custom count input handler (text message with number 1-100) in src/handlers/callbacks.py
- [ ] T036 [US3] Update photo processing flow: method selection → count selection → processing in src/handlers/photo.py

### Multi-Copy Generation

- [ ] T037 [US3] Implement generate_copies(image_bytes, count, method) in src/handlers/photo.py
- [ ] T038 [US3] Add progress callback for copy generation > 10 copies in src/handlers/photo.py
- [ ] T039 [US3] Implement send_result() in src/handlers/photo.py (single file if count=1, ZIP if count>1)
- [ ] T040 [US3] Add file naming convention: image_1.jpg, image_2.jpg, ... in generate_copies()

### Validation

- [ ] T041 [US3] Verify all generated copies have unique hashes (different from each other) in generate_copies()
- [ ] T042 [US3] Add 30-second timeout for count selection with default count=1 in src/handlers/callbacks.py

**Checkpoint**: Bot generates multiple unique copies and sends as ZIP when count > 1

---

## Phase 5: User Story 4 - Пакетная обработка (P2)

**Goal**: User sends album of images → all processed and returned separately

**Independent Test**: Send album of 5 images, verify each is uniqueized and returned

### Album Handling

- [ ] T043 [P] [US4] Add media_group collection logic in src/handlers/photo.py (2-second collection timeout)
- [ ] T044 [US4] Implement process_album(images: List[bytes]) in src/handlers/photo.py
- [ ] T045 [US4] Add album size validation (max 10 images) in src/handlers/photo.py
- [ ] T046 [US4] Add progress messages for album processing in src/handlers/photo.py

### Error Recovery

- [ ] T047 [US4] Implement partial success handling (continue processing if one image fails) in process_album()
- [ ] T048 [US4] Add per-image error messages in process_album()

**Checkpoint**: Bot handles albums up to 10 images with graceful error handling

---

## Phase 6: User Story 5 - Предпросмотр результата (P3)

**Goal**: User can preview result before receiving full file

**Independent Test**: Enable preview mode, send image, see thumbnail, confirm to get full file

### Preview Mode

- [ ] T049 [P] [US5] Add preview mode toggle in user session state in src/handlers/callbacks.py
- [ ] T050 [US5] Implement generate_preview(image_bytes) in src/utils/image.py (thumbnail ~300px)
- [ ] T051 [US5] Add preview confirmation keyboard (Confirm / Cancel) in src/handlers/callbacks.py
- [ ] T052 [US5] Update processing flow to show preview first when enabled in src/handlers/photo.py

**Checkpoint**: Users can preview results before downloading full resolution

---

## Phase 7: Polish & Integration

**Purpose**: Final integration and cleanup

- [ ] T053 [P] Update root bot.py to import from src/bot.py (backwards compatibility entry point)
- [ ] T054 [P] Add /help command with method descriptions in src/bot.py
- [ ] T055 [P] Add logging throughout all handlers and uniqueizers
- [ ] T056 [P] Create Dockerfile for deployment
- [ ] T057 Run manual integration test following quickstart.md scenarios
- [ ] T058 Code cleanup: remove old bot.py code, ensure consistent style

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - Core MVP
- **Phase 4 (US3)**: Depends on Phase 3 (needs photo handler flow)
- **Phase 5 (US4)**: Depends on Phase 3 (needs photo handler flow)
- **Phase 6 (US5)**: Depends on Phase 3 (needs processing flow)
- **Phase 7 (Polish)**: Depends on all desired user stories

### User Story Independence

| Story | Can Start After | Integrates With | Independent Test |
|-------|-----------------|-----------------|------------------|
| US1 (P1) | Phase 2 | None | Send image → select method → get result |
| US3 (P1) | US1 complete | US1 flow | Select count > 1 → get ZIP |
| US4 (P2) | US1 complete | US1 methods | Send album → get all processed |
| US5 (P3) | US1 complete | US1 flow | Enable preview → confirm → get file |

### Parallel Opportunities

**Phase 2 (all can run in parallel)**:
```
T006, T007, T008, T009, T010 - base infrastructure
T011, T012, T013 - uniqueizer implementations (different files)
```

**Phase 3 US1 (partial parallel)**:
```
T019, T020 - handler setup (different files)
```

**Multiple User Stories (after Phase 3)**:
```
US3, US4, US5 can be developed in parallel by different developers
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T018)
3. Complete Phase 3: US1 Method Selection (T019-T031)
4. **STOP and VALIDATE**: Test independently with real Telegram bot
5. Deploy if ready - users can select methods and get uniqueized images

### Incremental Delivery

1. Setup + Foundational → Engine ready
2. Add US1 → **MVP!** (method selection works)
3. Add US3 → Multiple copies + ZIP
4. Add US4 → Album support
5. Add US5 → Preview mode (nice-to-have)

---

## Summary

| Phase | Tasks | Purpose |
|-------|-------|---------|
| Phase 1 | T001-T005 (5) | Project setup |
| Phase 2 | T006-T018 (13) | Core engine + quality |
| Phase 3 (US1) | T019-T031 (13) | Method selection MVP |
| Phase 4 (US3) | T032-T042 (11) | Multi-copy + ZIP |
| Phase 5 (US4) | T043-T048 (6) | Album processing |
| Phase 6 (US5) | T049-T052 (4) | Preview mode |
| Phase 7 | T053-T058 (6) | Polish |
| **Total** | **58 tasks** | |

---

## Notes

- Tests not included (not explicitly requested)
- [P] = parallelizable (different files)
- Each phase checkpoint allows validation
- MVP = Phase 1 + 2 + 3 (23 tasks)
- Quality preservation (US2) integrated into Phase 2 foundational
