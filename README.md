## Running the app
Please remember to install the correct dependencies based on the `requirements.txt` in the backend and `pnpm install` for the frontend (navigate to the correct subfolder first).

You will need to add a `.env.local` file to the top of the webapp folder with the following variables as this is not being updated automatically with pnpm:

`NEXT_PUBLIC_SUPABASE_URL=https://nojcvxzcmqwmjfasalxh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vamN2eHpjbXF3bWpmYXNhbHhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA0MTU2NTAsImV4cCI6MjA0NTk5MTY1MH0.Wr44jWxWbtzGofMo0l2B2zoinV2ZcUwZGXqVkcgURIE
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_a25vd24tc2FpbGZpc2gtNDcuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_SECRET_KEY=sk_test_T8NrffV4Xp2DljfKgtoZVYcj8bbBUuxoIwsgfecSG5`

### Running the backend
`cd backend` -> `python app.py`

### Running the frontend
(in a new terminal)

`cd webapp` -> `pnpm dev`


