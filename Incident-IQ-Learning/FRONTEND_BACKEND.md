# Frontend-Backend Communication

The React frontend and FastAPI backend communicate via a RESTful API.

## Tools
- **TanStack Query**: The frontend uses this for fetching, caching, synchronizing, and updating server state. It simplifies handling loading states and errors compared to standard `useEffect` hooks.
- **Zod**: Used alongside React Hook Form for validating data on the frontend before it's even sent to the backend.
- **Pydantic**: Validates the exact same data structures once they arrive at the FastAPI backend.
