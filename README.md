# Real Estate Platform API

Welcome to the **Real Estate Platform API**. This API is designed to facilitate communication between real estate agents, property owners and clients.
This API provides endpoints for user registration, profile management, property management, real-time messaging and location based services.

## Features
- **User Authentication & Management**: User roles include clients, agents and property owners.
- **Property Listings**: Add, edit, search, and view property details.
- **Real-Time Messaging**: Real-time WebSocket-based messaging between clients and agents.
- **Notifications**: Users can subscribe to email notifications based on their preferences.
- **Geo-location Support**: Users can make property searches based on their geographical locations.
- **OTP-Based Verification**: Users are verified using OTP (One-Time Password) verification.
- **JWT-Based Authentication**: Protected endpoints can be accessed using a token
- **Search & Filter Properties**: Search for properties based on provided criteria such as city, state, price range, number of bedroom, and more.
- **Property Reviews & Ratings**: Leave and view property reviews
- **Agent Testimonials**: Clients can leave and view testimonials for agents

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Running Locally](#running-locally)
3. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication)
   - [Profile Management](#profile)
   - [Properties](#properties)
   - [Chat](#chat)
   - [Agent](#agent)
   - [Notifications](#notifications)
4. [User Roles](#user-roles)
5. [Technologies Used](#technologies-used)


---

## Getting Started

### Prerequisites
- Python 3.8+
- Django 4.0+
- Django Rest Framework
- PostreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/real_estate_app.git
   cd real_estate_app

2. Install the dependencies
   ```bash
   pip install -r requirements.txt
3. Create and configure your .env file with the necessary environment variables

4. Apply migrations:
   ```bash
   python manage.py migrate


## Running Locally
```bash
python manage.py runserver
```
---

## API Endpoints

### Authentication
 * POST /register - Register a new user
 * POST /login - Login with email and password
 * POST /forgot-password - Endpoint to intiate password recovery
 * POST /password-reset/{uidb64}/{token} - Password reset endpoint
 * POST /send-otp - Send OTP for verification
 * POST /verify-otp - Verify OTP sent

### Profile Management
 * GET /client/{client_id} - Get Client Details
 * GET /agent/{agent_id} - Get Agent Details
 * PATCH /update/{user_id} - Update user profile
 * PATCH /deactivate/{user_id} - Deactivate User Account
 * POST /reactivate - Send account activation link to User
 * POST /activate/{uidb64}/{token} - Activate User account

### Property Management
  * GET /properties - Get all properties. Can receive search queries too.
  * POST /properties/add - For Agents and Owners. Add a property
  * GET /properties/{id} - Get a details about a specific property
  * PATCH /properties/edit/{id} - Edit details about a property
  * DELETE /properties/delete/{id} - Delete a property
  * POST /properties-review - Post a review about a property

### Chat (WebSocket Connection)
  * /ws/chats/{conversation_id}/connect/{recepient_id} - Messages can be sent and received in real time

### Agent 
  * POST /agent-testimonial - Send in a testimonial of an agent
  * GET /agents/{agent_id}/testimonials - Get testimonials of an agent
  * GET /agents - Get/Search for all Agents registered on the platform

### Notifications
  * POST /notifications/subscribe - Subscribe to email alerts based on preference
  * GET /notifications/preferences - Get a users property preferences
  * DELETE /notifications/unsubscribe - Unsubscribe from email alerts

---

## User Roles
The platform supports multiple user roles:
1. **Client**: Can search for properties, contact agents, leave reviews and more.
2. **Agent**: Can list properties, receive messages from clients, and manage property listings
3. **Owner**: Can list and manage properties they own.

---

## Technologies Used
* **Django**: A Python Web Frameword for rapid developement.
* **Django Rest Framework**: For building the API.
* **Django Rest Framework Simple JWT**: For authenticating users with tokens.
* **Django Channels**: For handling WebSockets and real-time features
* **PostgreSQL**: A powerful, open-source object-relational database
* **Render**: For deployment of the API
