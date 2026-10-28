# AI workflow

## Tool

I used Claude to resolve questions and clarify uncertainties, review and refine the wording and logic of the DAX measures, and improve the documentation for the data model I built in Power BI, where all calculations and results were implemented and validated.

1. **DAX Measure Correction and Date Relationships**

   I asked whether it was correct to use `USERELATIONSHIP(fact_refund[refund_date], dim_date[date])` because I was unsure whether this would allow the measure to use `refund_date` while ignoring the date filter applied through the existing relationship.

2. **Business Logic: Definition of a Paying Client**

   I had a business logic question about the definition of a *paying client*: should it include everyone who has made a purchase, or only clients whose total payments minus refunds result in a positive net amount?

3. **Git Bash: Checking the Configured Email Address**

   I needed to verify which email address was configured in Git Bash, so I asked how to check it using `git config --global user.email`.

4. **AI-Assisted Documentation and DAX Validation**

   I used Claude to review and refine the wording and logic of the DAX measures, as well as to improve the documentation for the Power BI data model I built. All calculations, implementations, and results were validated within Power BI.

## Where the AI was confidently wrong

`[Co-Development Overlap]` was first proposed as
`[Studio Credited Net Revenue] - [Company Net Revenue]`. The total row was right (424,406.54), so it
looked correct. In the per-studio verification table, every studio row showed a large negative number
(e.g. Emberwatch −1,016,846.92): on a studio row, "studio credited" is one studio but "company" is the
whole company, so the subtraction means nothing. Fixed by removing the studio filter inside the measure,
so it shows the same overlap on every row.

## How I checked the numbers

Every scorecard value was read from a table visual built on the measures, with the filter stated in
`SCORECARD.md`, and checked against the business rules in the brief (e.g. the studio sum minus the
company total equals exactly the two co-developed titles).

## Parallel agents / worktrees

None. One model, built sequentially in one Power BI file.
