# hooks

React contexts and data access.

- `AuthContext.tsx` — `AuthProvider` / `useAuth`: session restore on load, sign
  in, sign out, and `expired` when the cookie stopped being accepted.
- `FiltersContext.tsx` — `FiltersProvider` / `useFilters`: the filter state
  shared by every screen, plus the chat and employee lists the dropdowns need
  and `reloadEmployees`, for after a write changes one.
- `useResource.ts` — loads one endpoint into `{ data, loading, error, reload }`
  and drops results from a stale request.
- `useTheme.ts` — light/dark, written to `data-theme` and `localStorage`.
- `useMediaQuery.ts` — `useMediaQuery` and `useBreakpoints`, for components that
  need a pixel value rather than a CSS rule.
- `usePagination.ts` — page and page size state, plus `useDebounced` for search
  input.

`useResource` re-runs on its dependency list; pages pass a serialized filter key
because the filter object is rebuilt on every render.

`usePagination` resets to page 1 whenever its reset key or the page size changes,
so a filter change cannot leave the list on a page that no longer exists.

`AuthProvider` owns the client's unauthorized handler and translates sign-in
failures into Uzbek; the server's English `detail` is never shown as is.
