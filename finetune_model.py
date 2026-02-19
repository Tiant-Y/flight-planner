# finetune_model.py
# Upload training data and start fine-tuning GPT-4o

import openai
import time
import json

# Initialize OpenAI client
client = openai.OpenAI()


def upload_training_file(filename="training_data.jsonl"):
    """Upload training data to OpenAI"""
    print("\n" + "═" * 70)
    print("  STEP 1: UPLOADING TRAINING DATA")
    print("═" * 70 + "\n")
    
    print(f"📤 Uploading {filename}...")
    
    with open(filename, "rb") as f:
        response = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    
    file_id = response.id
    print(f"✅ File uploaded successfully!")
    print(f"📋 File ID: {file_id}")
    print(f"📊 Status: {response.status}")
    
    return file_id


def start_finetuning(file_id, model="gpt-4o-mini-2024-07-18", suffix=None):
    """Start a fine-tuning job"""
    print("\n" + "═" * 70)
    print("  STEP 2: STARTING FINE-TUNING JOB")
    print("═" * 70 + "\n")
    
    print(f"🚀 Starting fine-tuning with model: {model}")
    
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=model,
        suffix=suffix  # Optional: adds a custom suffix to your model name
    )
    
    job_id = job.id
    print(f"✅ Fine-tuning job created!")
    print(f"📋 Job ID: {job_id}")
    print(f"📊 Status: {job.status}")
    
    return job_id


def monitor_finetuning(job_id, check_interval=60):
    """Monitor fine-tuning progress"""
    print("\n" + "═" * 70)
    print("  STEP 3: MONITORING FINE-TUNING PROGRESS")
    print("═" * 70 + "\n")
    
    print("⏳ Fine-tuning in progress... This typically takes 10-60 minutes.")
    print(f"🔄 Checking status every {check_interval} seconds.\n")
    
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status
        
        print(f"[{time.strftime('%H:%M:%S')}] Status: {status}")
        
        if status == "succeeded":
            print("\n🎉 Fine-tuning completed successfully!")
            print(f"✅ Your custom model: {job.fine_tuned_model}")
            return job.fine_tuned_model
        
        elif status == "failed":
            print("\n❌ Fine-tuning failed!")
            print(f"Error: {job.error}")
            return None
        
        elif status in ["validating_files", "queued", "running"]:
            # Still in progress
            time.sleep(check_interval)
        
        else:
            print(f"\n⚠️  Unexpected status: {status}")
            time.sleep(check_interval)


def list_finetuning_jobs(limit=5):
    """List recent fine-tuning jobs"""
    print("\n" + "═" * 70)
    print("  YOUR RECENT FINE-TUNING JOBS")
    print("═" * 70 + "\n")
    
    jobs = client.fine_tuning.jobs.list(limit=limit)
    
    if not jobs.data:
        print("No fine-tuning jobs found.")
        return
    
    for job in jobs.data:
        print(f"Job ID: {job.id}")
        print(f"  Model: {job.model}")
        print(f"  Status: {job.status}")
        if job.fine_tuned_model:
            print(f"  Fine-tuned Model: {job.fine_tuned_model}")
        print(f"  Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(job.created_at))}")
        print()


def test_finetuned_model(model_name, test_query="What's the MTOW of a Boeing 777-300ER?"):
    """Test your fine-tuned model with a sample query"""
    print("\n" + "═" * 70)
    print("  TESTING YOUR FINE-TUNED MODEL")
    print("═" * 70 + "\n")
    
    print(f"🧪 Testing model: {model_name}")
    print(f"❓ Test query: {test_query}\n")
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert AI flight planning assistant."},
            {"role": "user", "content": test_query}
        ]
    )
    
    print("🤖 Response:")
    print("─" * 70)
    print(response.choices[0].message.content)
    print()


def complete_finetuning_workflow(
    training_file="training_data.jsonl",
    model="gpt-4o-mini-2024-07-18",
    suffix="flight-planner",
    monitor=True
):
    """
    Complete end-to-end fine-tuning workflow:
    1. Upload training data
    2. Start fine-tuning job  
    3. Monitor progress (optional)
    4. Test the model
    """
    
    print("\n" + "═" * 70)
    print("  🚀 STARTING COMPLETE FINE-TUNING WORKFLOW")
    print("═" * 70)
    
    # Step 1: Upload file
    file_id = upload_training_file(training_file)
    
    # Step 2: Start fine-tuning
    job_id = start_finetuning(file_id, model, suffix)
    
    print(f"\n📧 You'll receive an email when fine-tuning completes.")
    print(f"📋 Job ID: {job_id}")
    
    if monitor:
        # Step 3: Monitor progress
        model_name = monitor_finetuning(job_id)
        
        if model_name:
            # Step 4: Test the model
            print("\n" + "═" * 70)
            print("  ✅ FINE-TUNING COMPLETE!")
            print("═" * 70)
            print(f"\nYour custom model name: {model_name}")
            print("\nYou can now use this model in your code:")
            print(f'  client.chat.completions.create(model="{model_name}", messages=[...])')
            
            # Quick test
            test = input("\n🧪 Test the model now? (y/n): ").strip().lower()
            if test == 'y':
                test_finetuned_model(model_name)
        else:
            print("\n❌ Fine-tuning failed. Check the error above.")
    
    else:
        print("\n⏭️  Monitoring skipped. Check status later with:")
        print(f'  python -c "import openai; print(openai.OpenAI().fine_tuning.jobs.retrieve(\'{job_id}\'))"')


# ── COST ESTIMATOR ────────────────────────────────────────────────────────────
def estimate_finetuning_cost(training_file="training_data.jsonl"):
    """Estimate the cost of fine-tuning based on your training data"""
    print("\n" + "═" * 70)
    print("  💰 COST ESTIMATION")
    print("═" * 70 + "\n")
    
    # Count tokens approximately
    total_tokens = 0
    example_count = 0
    
    with open(training_file, 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            # Rough estimate: ~4 characters per token
            for msg in example['messages']:
                total_tokens += len(msg['content']) // 4
            example_count += 1
    
    print(f"📊 Training Data Statistics:")
    print(f"  Examples: {example_count}")
    print(f"  Estimated tokens: {total_tokens:,}")
    
    # GPT-4o-mini fine-tuning cost (as of 2024)
    # Training: $3.00 / 1M tokens
    # Input: $0.30 / 1M tokens  
    # Output: $1.20 / 1M tokens
    
    training_cost = (total_tokens / 1_000_000) * 3.00
    
    print(f"\n💵 Estimated Costs:")
    print(f"  Training cost: ${training_cost:.2f}")
    print(f"  (This is a one-time cost to create your custom model)")
    
    print(f"\n💡 After fine-tuning, using your model costs:")
    print(f"  Input: $0.30 per 1M tokens")
    print(f"  Output: $1.20 per 1M tokens")
    print(f"  (Same as base GPT-4o-mini)")


# ── MAIN MENU ─────────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 70)
    print("  GPT-4O FINE-TUNING MENU")
    print("═" * 70)
    print("\n1. Complete workflow (upload + train + monitor)")
    print("2. Upload training file only")
    print("3. List my fine-tuning jobs")
    print("4. Check job status")
    print("5. Test a fine-tuned model")
    print("6. Estimate fine-tuning cost")
    print("7. Exit")
    
    choice = input("\nSelect option (1-7): ").strip()
    
    if choice == "1":
        complete_finetuning_workflow()
    
    elif choice == "2":
        file_id = upload_training_file()
        print(f"\n✅ File uploaded. File ID: {file_id}")
        print("Use this file ID to start fine-tuning manually.")
    
    elif choice == "3":
        list_finetuning_jobs()
    
    elif choice == "4":
        job_id = input("Enter job ID: ").strip()
        job = client.fine_tuning.jobs.retrieve(job_id)
        print(f"\nJob Status: {job.status}")
        if job.fine_tuned_model:
            print(f"Model: {job.fine_tuned_model}")
    
    elif choice == "5":
        model_name = input("Enter fine-tuned model name: ").strip()
        test_finetuned_model(model_name)
    
    elif choice == "6":
        estimate_finetuning_cost()
    
    elif choice == "7":
        print("\nGoodbye! ✈️")
    
    else:
        print("\n❌ Invalid option")


if __name__ == "__main__":
    import sys
    
    # If run without arguments, show menu
    if len(sys.argv) == 1:
        main()
    
    # Quick mode: python finetune_model.py --auto
    elif "--auto" in sys.argv:
        complete_finetuning_workflow(monitor=True)
    
    # Estimate mode: python finetune_model.py --estimate
    elif "--estimate" in sys.argv:
        estimate_finetuning_cost()
    
    else:
        print("Usage:")
        print("  python finetune_model.py           # Interactive menu")
        print("  python finetune_model.py --auto    # Automatic workflow")
        print("  python finetune_model.py --estimate # Estimate cost")
