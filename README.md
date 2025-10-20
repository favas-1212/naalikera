Daily Wage Worker Platform

A full-stack platform connecting customers with daily wage workers, allowing booking, reviews, and real-time availability management.


---

🚀 Features

Authentication

User/Worker registration & login with JWT

OTP verification for phone

Password reset & logout

JWT refresh token support


Customer

Browse job categories

Search workers by category, location, price, and rating

Booking management (create, cancel, view)

Submit reviews & ratings

Profile management


Worker

Create/update profile

Set availability and pricing

Manage bookings (accept/decline)

Track earnings

Upload ID/certificates

Update online/busy/offline status


Admin

Approve/reject worker registrations

Manage users and workers

Modify/cancel bookings

Analytics & reports

Manage job categories


Notifications

Real-time notifications

Mark as read

Update notification preferences



---

📋 API Endpoints

Authentication

Method	Endpoint	Description

POST	/api/auth/register	User/Worker registration
POST	/api/auth/login	Login (returns JWT token)
POST	/api/auth/verify-otp	OTP verification
POST	/api/auth/forgot-password	Password reset request
POST	/api/auth/logout	Logout & invalidate token
GET	/api/auth/refresh-token	Refresh JWT token


Customer APIs

Method	Endpoint	Description

GET	/api/categories	List job categories
GET	/api/workers/search	Search workers (filters: category, location, price, rating)
GET	/api/workers/:id	Get worker profile details
POST	/api/bookings	Create new booking
GET	/api/bookings	Get customer's bookings
GET	/api/bookings/:id	Get specific booking details
PUT	/api/bookings/:id/cancel	Cancel booking
POST	/api/reviews	Submit review & rating
GET	/api/customers/profile	Get customer profile
PUT	/api/customers/profile	Update customer profile


Worker APIs

Method	Endpoint	Description

POST	/api/workers/profile	Create/Update profile
GET	/api/workers/profile	Get own profile
PUT	/api/workers/availability	Update availability calendar
PUT	/api/workers/pricing	Update pricing
GET	/api/workers/bookings	Get worker bookings
PUT	/api/bookings/:id/accept	Accept booking request
PUT	/api/bookings/:id/decline	Decline booking request
PUT	/api/workers/status	Update online/busy/offline status
GET	/api/workers/earnings	Get earnings history
GET	/api/workers/reviews	Get received reviews
POST	/api/workers/documents	Upload ID/certificates


Admin APIs

Method	Endpoint	Description

GET	/api/admin/workers/pending	List pending worker approvals
PUT	/api/admin/workers/:id/approve	Approve worker
PUT	/api/admin/workers/:id/reject	Reject worker
GET	/api/admin/users	List all users
GET	/api/admin/workers	List all workers
PUT	/api/admin/users/:id/ban	Ban/Unban user
DELETE	/api/admin/users/:id	Delete user account
GET	/api/admin/bookings	List all bookings
PUT	/api/admin/bookings/:id	Modify/cancel booking
GET	/api/admin/analytics	Dashboard analytics
GET	/api/admin/reports	Generate PDF/Excel reports
GET	/api/admin/categories	Manage job categories
POST	/api/admin/categories	Add new category


Notification APIs

Method	Endpoint	Description

GET	/api/notifications	Get user notifications
PUT	/api/notifications/:id/read	Mark notification as read
POST	/api/notifications/settings	Update notification preferences



---

🛠 Frontend (React) Setup

1. Clone Repository

git clone https://github.com/yourusername/daily-wage-platform.git
cd daily-wage-platform/frontend

2. Install Dependencies

npm install

3. Create Environment File

Create .env in frontend:

REACT_APP_API_BASE_URL=http://localhost:8000/api

4. Run Development Server

npm start

Access at: http://localhost:3000

5. Build for Production

npm run build


---

🔧 Recommended Frontend Libraries

React Router DOM (Routing)

Axios (API calls)

Redux/Context API (State management)

Material UI / Tailwind CSS (UI Components)

React Hook Form (Forms)

JWT Decode (Authentication)



---

📌 Notes

Ensure backend API is running and accessible from frontend.

Use JWT token in Authorization header for protected endpoints.

Worker availability and pricing can be updated in real-time.
