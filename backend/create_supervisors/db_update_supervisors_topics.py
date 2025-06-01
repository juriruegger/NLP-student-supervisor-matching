from backend.create_supervisors.utils import valid_supervisor_topic

def db_update_supervisors_topics(supabase, supervisors, topics, supervisor_topics):
    """
    Update the supervisors, topics and the supervisor_topic relations in the database.
    """
    # Updating the DB
    batch_size = 5 # We're upserting in batches to avoid size limitations

    for i in range(0, len(supervisors), batch_size):
        batch = supervisors[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            response = (
                supabase.table("supervisor")
                .upsert(batch)
                .execute()
            )
        except Exception as e:
            print(f"Error in batch {batch_num}: {str(e)},")

    # Delete all old topics and supervisor_topic relations
    supabase.table("supervisor_topic").delete().neq("uuid", "1").execute()
    supabase.table("topic").delete().neq("label", "1").execute()

    # Insert new topics
    if topics:
        supabase.table("topic").insert(topics).execute()

    valid_supervisor_topics = [
        supervisor_topic for supervisor_topic in supervisor_topics
        if valid_supervisor_topic(supervisor_topic["topic_id"]) and valid_supervisor_topic(supervisor_topic["score"])
    ]

    if valid_supervisor_topics:
        supabase.table("supervisor_topic").insert(valid_supervisor_topics).execute()