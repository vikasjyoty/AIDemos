# Tool Testing Prompts

Use these prompts directly in your Strands agent chat. They are grouped by tool type and then mixed workflows.

## How to use

- Run from Strands-Agent with your model configured.
- Paste one prompt at a time.
- Observe which tool(s) the agent selects and the returned structured output.

## 1) Database Tools (db_tools.py)

### Prompt 1
Save a contact with name Ravi, email ravi@example.com, and phone +919999999999.

### Prompt 2
Fetch the contact details for Ravi.

### Prompt 3
Update Ravi with email ravi.kumar@example.com and phone +919888888888.

### Prompt 4
List the latest 5 contacts.

### Prompt 5
Try fetching a contact named Unknown Person and tell me if it exists.

## 2) API Tools (api_tools.py)

### Prompt 1
Look up mock customer profile for customer id CUST-1024.

### Prompt 2
Call this API and summarize its JSON response: https://api.github.com

### Prompt 3
Call this API URL and show me status and key fields: https://jsonplaceholder.typicode.com/todos/1

### Prompt 4
Try calling https://example.com and explain why it may be blocked by policy.

### Prompt 5
For customer id CUST-2031, fetch mock data and tell me if tier is gold or standard.

## 3) Notification Tools (notification_tools.py)

### Prompt 1
Send an SMS to +14155552671 saying Deployment completed successfully.

### Prompt 2
Send an email to ops@example.com with subject Daily Health Check and body All services are healthy.

### Prompt 3
Post a Slack message to #alerts saying Build pipeline is green.

### Prompt 4
Try sending SMS to 123 and explain validation error.

### Prompt 5
Send an email to wrong-email-format with subject Test and body test.

## 4) Calendar Tools (calendar_tools.py)

### Prompt 1
Create a calendar event titled Team Sync at 2026-07-22T10:00:00Z for 45 minutes.

### Prompt 2
Create an event titled Customer Demo at 2026-07-23T14:30:00Z for 60 minutes.

### Prompt 3
List the latest 10 calendar events.

### Prompt 4
Try creating an event with start time tomorrow at ten and explain why format fails.

### Prompt 5
Create an event called Standup at 2026-07-24T04:30:00Z for 15 minutes.

## 5) Human-in-the-Loop Tools (human_in_loop_tools.py)

### Prompt 1
Request human approval for action Refund order #12345 with reason Customer reported duplicate charge.

### Prompt 2
Approve request id apr_replace_me as approver Vikas.

### Prompt 3
Execute sensitive action using approval id apr_replace_me with payload refund 49.99 USD.

### Prompt 4
Try executing sensitive action with approval id apr_not_exist and payload test.

### Prompt 5
Create an approval request for Delete customer record CUST-9001 with reason GDPR data removal request.

## 6) Mixed Multi-Tool Scenarios

### Scenario 1: CRM style flow (DB + Notification)
Save contact Priya with email priya@example.com and phone +14155550111, then send her an SMS saying Welcome to the service.

### Scenario 2: Incident flow (API + Slack)
Call https://jsonplaceholder.typicode.com/todos/1, summarize result in one line, then post that summary to #alerts.

### Scenario 3: Meeting setup flow (DB + Calendar + Email)
Save contact Arun with email arun@example.com, create a meeting called Onboarding Sync at 2026-07-25T09:00:00Z for 30 minutes, then send Arun an email with the meeting details.

### Scenario 4: Approval-gated action (Human-in-loop + Notification)
Request approval for action Send outage notification to all customers with reason Production outage severity high, then after approval send a Slack update to #alerts.

### Scenario 5: Customer follow-up (API + DB + Email)
Get mock customer info for CUST-2026, save contact as Customer CUST-2026 with placeholder email cust2026@example.com, then send a follow-up email with a short status update.

### Scenario 6: Data verification flow (DB + API)
Save contact Neha with email neha@example.com and phone +14155550999, fetch her record, then also fetch mock customer info for CUST-5555 and compare if both are active records.

### Scenario 7: Operations handoff (Calendar + Slack + Email)
Create event Incident Review at 2026-07-26T12:00:00Z for 60 minutes, then post reminder in #alerts and send email to ops@example.com with the event details.

### Scenario 8: Safety check flow (Human-in-loop + Execute)
Create an approval request for Refund order #9090 reason Customer charged twice, try to execute before approval and report blocked status, then approve and execute successfully.

## 7) Advanced Prompt Style (Agentic Planning)

Use these to encourage multi-step reasoning and tool orchestration.

### Prompt A
You are an operations assistant. Create a concise action plan, execute tools step by step, and show final summary. Task: fetch a sample API record, store a related contact in DB, notify #alerts, and email ops@example.com.

### Prompt B
Act with approval safety. For any sensitive operation, first request human approval, wait for approval id handling, then execute and return an audit summary.

### Prompt C
Perform this workflow and show intermediate tool outputs: create two contacts, schedule one meeting, send one SMS reminder, and list current contacts and events.

## 8) Notes for Human-in-the-Loop Prompts

- Replace apr_replace_me with the real approval id returned by your previous approval request.
- The in-memory approval store resets when the app restarts.

## 9) Expected Behavior Checklist

- DB prompts should return structured contact data.
- API prompts should enforce allowlist and return errors for blocked hosts.
- Notification prompts should validate phone/email/channel formats.
- Calendar prompts should enforce ISO datetime input.
- Human-in-the-loop prompts should block sensitive execution until approved.
- Mixed scenarios should chain multiple tools in one run when model behavior allows it.
