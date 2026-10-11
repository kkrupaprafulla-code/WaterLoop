# WATERLOOP 💧
### Make Every Litre Count.

WATERLOOP is a water-reuse decision-support prototype that helps facility managers plan how available treated wastewater can be allocated across different non-potable uses.

Instead of only displaying water availability, WATERLOOP helps users understand allocation priorities, manage shortages, estimate potential freshwater displacement, and explore the financial impact of water reuse.

> **Our mission:** Turn water availability into smarter water-allocation decisions.

---

## 🚨 The Problem

Water scarcity is a serious challenge for cities and industries. At the same time, treated wastewater may be available for suitable non-potable applications.

Facilities need to make practical decisions:

- Which uses should receive available reused water first?
- What happens when water supply falls below total demand?
- How much demand can be fulfilled?
- What is the estimated financial value of the freshwater that could be displaced?

WATERLOOP explores these questions through an interactive water-allocation planner.

## 💡 Our Solution

WATERLOOP provides an interactive decision-support interface that allows users to:

- Explore a representative facility's water supply and demand.
- Allocate available water according to configurable priorities.
- Simulate water shortages.
- Review prototype water-quality checks.
- Place allocations on hold when the frontend quality checks fail.
- Estimate potential freshwater displacement and gross financial savings.
- Access allocation calculations through an AWS Lambda Function URL.

## ✨ Key Features

### 1. Priority-Based Water Allocation

Water demand is allocated according to priority, helping higher-priority uses receive water before lower-priority uses.

### 2. Shortage Simulation

Reduce the available supply and observe how allocations change when demand exceeds supply.

### 3. Prototype Quality Checks

The current prototype checks turbidity and pH for a toilet-flushing scenario.

These checks are preliminary decision-support checks, not proof that water is safe or suitable for reuse.

### 4. Impact Estimation

Estimate potential freshwater displacement and gross financial savings using an adjustable assumed water price.

### 5. AWS Integration

The frontend sends allocation requests to an AWS Lambda Function URL and displays the returned allocation results.

### 6. Interactive Dashboard

Explore supply, demand, allocations, remaining water, and estimated financial impact through a single interface.

## 🛠️ Technology Stack

- **Frontend:** React, Vite, JavaScript, CSS
- **Backend:** Python
- **Cloud:** AWS Lambda and Lambda Function URL
- **Testing:** Python unit tests and frontend scenario testing
- **Version Control:** Git and GitHub

## 🏗️ Architecture

1. The user selects a water-supply scenario and reviews the demand data.
2. The frontend performs its prototype quality checks.
3. If those checks fail, the frontend holds the displayed allocations.
4. Otherwise, the frontend sends an allocation request to AWS Lambda.
5. Lambda calculates the priority-based allocation and returns the result.
6. The interface displays allocations and estimated impact.

**Important implementation detail:** The current Lambda allocation handler does not independently enforce the frontend's water-quality checks. The quality gate is implemented in the frontend. This prototype must not be treated as a production water-management or safety system.

## 🧪 Representative Demo Scenario

WATERLOOP uses illustrative figures for a fictional facility called **Metro Industrial Park**.

| Non-potable use | Daily demand | Priority |
|---|---:|---:|
| Toilet flushing | 80,000 L | 3 |
| Landscaping | 100,000 L | 2 |
| Vehicle exterior washing | 70,000 L | 1 |
| **Total** | **250,000 L** | |

### Normal Supply

With 500,000 litres available per day:

- Allocated: 250,000 L
- Remaining supply: 250,000 L
- Estimated gross savings: ₹12,500/day at an assumed price of ₹50 per 1,000 litres

### Water Shortage

With only 150,000 litres available per day:

- Toilet flushing: 80,000 L
- Landscaping: 70,000 L
- Vehicle exterior washing: 0 L
- Total allocated: 150,000 L

These figures demonstrate the allocation logic; they are not live facility data.

## 💰 Impact Calculation

The current prototype estimates gross savings using:

`Estimated gross savings = allocated reused water (L) / 1,000 × assumed price per 1,000 L`

The calculation assumes each litre of reused water displaces one litre of freshwater.

It excludes treatment, pumping, conveyance, maintenance, and other operating costs. The result is an illustrative estimate, not a verified financial saving.

## 🚀 Running the Project Locally

### Prerequisites

- Node.js and npm
- Python 3
- Git (optional, for version control)

### 1. Start the frontend

Open a terminal in the `frontend` directory and run:

```bash
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

If port 5173 is already in use, Vite may select another port. The AWS Function URL's CORS configuration must permit that origin for browser requests to succeed.

### 2. Run the Python tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

Use the Python environment in which the project's dependencies are installed.

### 3. AWS configuration

The current frontend connects to an AWS Lambda Function URL configured for the demo.

For local development, ensure the Function URL's CORS configuration permits the frontend's origin and the required request method and headers.

Do not commit AWS credentials, access keys, passwords, or other secrets to the repository.

## 📁 Project Structure

```text
WaterLoop/
├── backend/
│   ├── allocation/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── impact/
│   │   ├── __init__.py
│   │   └── calculator.py
│   ├── quality/
│   │   ├── models.py
│   │   ├── rules.py
│   │   └── validator.py
│   └── planner.py
├── frontend/
├── tests/
│   ├── test_engine.py
│   ├── test_planner.py
│   └── test_quality_validator.py
├── .gitignore
└── README.md
```

*The structure above highlights the main application components and tests. The frontend contains the React application.*


## ⚠️ Limitations and Responsible Use

- This is a hackathon prototype using representative data.
- It does not use live facility measurements or live water-demand feeds.
- Passing the current turbidity and pH checks does not establish that water is safe for a particular use.
- Applicable water-quality requirements depend on the intended use and must be verified independently.
- The current AWS Lambda handler performs allocation calculations but does not independently enforce the frontend quality gate.
- Financial estimates exclude operational and infrastructure costs.
- WATERLOOP is decision-support software, not a water-safety certification system.

## 🌍 Potential Future Improvements

- Integrate validated water-quality datasets and use-specific rules.
- Enforce quality eligibility in the backend before permitting allocation.
- Add persistent storage for facilities, scenarios, and historical decisions.
- Integrate verified local water-supply and demand data.
- Add audit logs, authentication, and role-based access.
- Improve cost estimation using treatment and distribution costs.
- Deploy a production-ready application with appropriate security and monitoring.

## 📚 References

Central Pollution Control Board (CPCB), *Guidelines for Reuse of Treated Sewage*:

[Read the CPCB guidelines](https://cpcb.nic.in/openpdffile.php?id=TmV3c0ZpbGVzLzEwNV8xNzA3Mzc4MTYwX21lZGlhcGhvdG8yMDUzNC5wZGY%3D)

The applicable requirements should be checked against the original document and the intended water-reuse application.

## 🤝 Built For

**WeMakeDevs AWS Environmental Hacks — 2026**

WATERLOOP explores how software and cloud computing can support more thoughtful water reuse and allocation decisions.
