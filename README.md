## Running the app
Please remember to install the correct dependencies based on the `requirements.txt` in the backend and `pnpm install` for the frontend (navigate to the correct subfolder first).

You must add a `.env.local` file to the top of the webapp folder and the top of the backend folder with the following variables. The openai api key is unnecessary to run the application and is only used for testing purposes.

#### Webapp
`NEXT_PUBLIC_SUPABASE_URL=https://nojcvxzcmqwmjfasalxh.supabase.co`

`NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vamN2eHpjbXF3bWpmYXNhbHhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA0MTU2NTAsImV4cCI6MjA0NTk5MTY1MH0.Wr44jWxWbtzGofMo0l2B2zoinV2ZcUwZGXqVkcgURIE`

`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_a25vd24tc2FpbGZpc2gtNDcuY2xlcmsuYWNjb3VudHMuZGV2JA`

`CLERK_SECRET_KEY=sk_test_T8NrffV4Xp2DljfKgtoZVYcj8bbBUuxoIwsgfecSG5`

`PURE_API=7624b829-efa4-4b7f-8e3d-4fcb295bd819`

`PURE_BASE_URL="https://pure.itu.dk/ws/api"`

`BACKEND_URL=http://127.0.0.1:5000/api`

#### backend
`PURE_API_KEY="7624b829-efa4-4b7f-8e3d-4fcb295bd819"`

`PURE_BASE_URL="https://pure.itu.dk/ws/api"`

`NEXT_PUBLIC_SUPABASE_URL="https://nojcvxzcmqwmjfasalxh.supabase.co"`

`NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vamN2eHpjbXF3bWpmYXNhbHhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA0MTU2NTAsImV4cCI6MjA0NTk5MTY1MH0.Wr44jWxWbtzGofMo0l2B2zoinV2ZcUwZGXqVkcgURIE"`

`OPENAI_API_KEY="<Provide your own api key>"`


### Running the backend
`cd backend` -> `python app.py`

### Running the frontend
(in a new terminal)

`cd webapp` -> `pnpm dev`


## Setup
The prototype uses shadcn/ui for components, tailwind for styling, and is built on the next.js app router architecture. It uses Clerk as the authentication provider and Supabase as the database provider.

The database architecture is as follows
![Supabase Schema (3)](https://github.com/user-attachments/assets/0baca369-06c4-458c-9b50-a6ca1caaa040)



