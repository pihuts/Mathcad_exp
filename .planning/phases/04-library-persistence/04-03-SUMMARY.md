# Plan 04-03 Summary: Frontend Library API and React Query Hook

**Date:** 2026-01-27
**Status:** Completed
**Wave:** 2

## Overview

Implemented type-safe frontend API service and React Query hook for library persistence operations (save, list, load). This provides the foundation for UI components to interact with the backend library endpoints created in plan 04-02.

## Implementation Details

### 1. TypeScript Types (frontend/src/services/api.ts)

Added complete TypeScript interfaces matching backend Pydantic schemas exactly:

- **LibraryConfigMetadata**: Config metadata (name, path, created_at, version)
- **ListLibraryConfigsResponse**: Wrapper for configs array
- **SaveLibraryConfigRequest**: Request payload for saving configs
- **SaveLibraryConfigResponse**: Response with status and config metadata
- **LoadLibraryConfigRequest**: Request with config_path
- **LoadLibraryConfigResponse**: Type alias to SaveLibraryConfigRequest (BatchConfig structure)

**Key Design Decision:** Used type alias (`LoadLibraryConfigResponse = SaveLibraryConfigRequest`) because the backend returns a BatchConfig object which has the same structure as the save request.

### 2. API Functions (frontend/src/services/api.ts)

Implemented three axios-based API functions:

```typescript
// Save a config to library
saveLibraryConfig(config: SaveLibraryConfigRequest): Promise<SaveLibraryConfigResponse>

// List all configs for a given file
listLibraryConfigs(filePath: string): Promise<ListLibraryConfigsResponse>

// Load a config from library
loadLibraryConfig(configPath: string): Promise<LoadLibraryConfigResponse>
```

**Integration Points:**
- All functions use the shared `api` axios instance with baseURL `/api/v1`
- Functions call `/library/save`, `/library/list`, `/library/load` endpoints
- Proper typing for request/response ensures type safety throughout the stack

### 3. React Query Hook (frontend/src/hooks/useLibrary.ts)

Created `useLibrary` hook with caching and error handling:

**Features:**
- **Cached Listing:** 5-minute staleTime for config lists (reduces redundant API calls)
- **Conditional Query:** Only fetches when filePath is provided (`enabled: !!filePath`)
- **Automatic Invalidation:** Save mutation invalidates list query to refresh data
- **Error Handling:** Exposes error states for UI feedback
- **Loading States:** Separate loading states for list, save, and load operations

**Hook API:**
```typescript
const {
  // List configs
  configs,
  isLoadingConfigs,
  listError,
  refetchConfigs,

  // Save config
  saveConfig,
  isSaving,
  saveError,
  saveResult,

  // Load config
  loadConfig,
  isLoadingConfig,
  loadError,
  loadedConfig,
} = useLibrary(filePath);
```

## Type Mapping Decisions

### Backend to Frontend Type Alignment

| Backend (Pydantic) | Frontend (TypeScript) | Notes |
|-------------------|----------------------|-------|
| `LibraryConfigMetadata` | `LibraryConfigMetadata` | Exact field match |
| `ListLibraryConfigsResponse` | `ListLibraryConfigsResponse` | Exact field match |
| `SaveLibraryConfigRequest` | `SaveLibraryConfigRequest` | Exact field match |
| `SaveLibraryConfigResponse` | `SaveLibraryConfigResponse` | Exact field match |
| `LoadLibraryConfigRequest` | `LoadLibraryConfigRequest` | Exact field match |
| `BatchConfig` | `LoadLibraryConfigResponse` | Type alias to SaveLibraryConfigRequest |

**Key Decision:** InputConfig is already defined in api.ts and reused for SaveLibraryConfigRequest.inputs field, matching the backend's reuse of InputConfig dataclass.

## Verification

### Build Verification
```bash
cd frontend && npm run build
```
- Result: Build successful with no TypeScript errors
- Note: Vite warning about chunk size is expected (not related to this work)

### Type Safety Verification
- All TypeScript interfaces match backend schemas exactly
- API functions properly typed for request/response
- useLibrary hook provides typed return values
- No implicit any types in library code

## Key Links Established

1. **api.ts → Backend API:**
   - `api.post('/library/save')` → `POST /api/v1/library/save`
   - `api.get('/library/list')` → `GET /api/v1/library/list`
   - `api.post('/library/load')` → `POST /api/v1/library/load`

2. **useLibrary → api.ts:**
   - Imports: `saveLibraryConfig`, `listLibraryConfigs`, `loadLibraryConfig`
   - Types: `SaveLibraryConfigRequest`, `LibraryConfigMetadata`

## Success Criteria Met

- [x] api.ts has saveLibraryConfig, listLibraryConfigs, loadLibraryConfig functions
- [x] TypeScript interfaces match backend schemas exactly
- [x] useLibrary hook provides list/save/load operations
- [x] useLibrary uses React Query for caching (5-minute staleTime)
- [x] List query invalidates after successful save
- [x] Frontend builds without type errors

## Next Steps

Plan 04-04 will create the LibraryModal UI component that uses this hook to provide:
- Save config dialog (name input + save button)
- Config list dropdown (using configs from hook)
- Load config button (using loadConfig from hook)
- Delete config functionality

## Files Modified

1. `frontend/src/services/api.ts` - Added library types and API functions (53 lines)
2. `frontend/src/hooks/useLibrary.ts` - Created React Query hook (67 lines)

## Commits

1. `feat(04-03): add library TypeScript types and API functions to api.ts`
2. `feat(04-03): create useLibrary React Query hook`
