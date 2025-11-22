# KrushiRakshak: Smart Farming Assistant
## Farmer Advisory and Risk Management System

---

**Project Team:** [Team Name Placeholder]  
**Date:** [Date Placeholder]  
**Version:** 1.0.0

---

## Abstract

KrushiRakshak is a web app built to help Indian farmers get better information about their crops. We combine weather data from IMD, satellite images from Bhuvan, market prices from Agmarknet, and let farmers share knowledge with each other. The app works on phones and computers, and it even works when there's no internet.

The app has an AI chatbot that answers farming questions instantly, a smart system that gives crop-specific advice, and a community section where farmers can share tips and ask questions. It's available in multiple languages and designed for mobile phones first. Our goal is to help farmers make better decisions so they can grow more crops, avoid losses, and earn more money.

---

## Problem Statement

Indian farmers face many problems that hurt their crops and income:

### 1. **No Real-Time Information**
- Farmers don't get weather updates on time, so crops get damaged by unexpected rain or storms
- Market prices are hard to find, so farmers sell their crops for less money
- There's no easy way to check if crops are healthy, so pests and diseases are found too late

### 2. **Information is Scattered**
- Weather, prices, and farming advice are on different websites and apps
- No single place has everything farmers need
- Farmers waste time checking multiple sources

### 3. **Too Complicated**
- Most apps are hard to understand for farmers who aren't tech-savvy
- The information is too technical and confusing
- Many apps are only in English, so farmers who speak other languages can't use them

### 4. **Internet Problems**
- Villages often have slow or no internet
- Apps stop working when farmers are in the field and need information most
- Most farming apps don't work without internet

### 5. **No Community Help**
- Farmers work alone without easy ways to talk to other farmers
- There's no place where farmers can share tips and ask questions
- Local farming knowledge stays in one place and doesn't spread

### 6. **Can't Predict Problems**
- Farmers don't have tools to see problems coming
- No system warns farmers about pests, diseases, or bad weather early
- Advice given to farmers is the same for everyone, not customized to their specific farm

Because of these problems, farmers grow less crops, lose money, and don't trust new technology. We need one simple app that solves all these problems together.

---

## Objectives

What we want to achieve with KrushiRakshak:

### 1. **Put Everything in One Place**
- Combine weather, satellite images, market prices, and crop health into one app
- Give personalized advice for each crop based on current conditions
- Tell farmers exactly what to do for pests, watering, and crop care

### 2. **Make It Easy to Use**
- Build a web app that works on phones and computers without complicated installation
- Make it work even when there's no internet
- Support multiple languages (English, Marathi) so more farmers can use it
- Design it so simple that anyone can use it, even without tech knowledge

### 3. **Help Farmers Make Better Decisions**
- Show weather forecasts and warnings for their specific location
- Display current market prices and trends so farmers know when to sell
- Check crop health using satellite data (NDVI)
- Warn farmers early about pests, diseases, or bad weather

### 4. **Let Farmers Help Each Other**
- Create a place where farmers can share tips and experiences
- Let farmers ask questions and get answers from other farmers
- Help farmers in different regions share knowledge
- Build a community where farmers support each other

### 5. **Use AI to Answer Questions**
- Add an AI chatbot that answers farming questions instantly
- Make sure the answers are simple and easy to understand
- Available 24/7 so farmers can ask questions anytime

### 6. **Make It Fast and Reliable**
- Build a strong backend that can handle many users at once
- Store data efficiently so it loads fast
- Design it to grow as more farmers start using it

### 7. **Help Farmers Use Resources Wisely**
- Encourage farmers to use data to avoid wasting water, fertilizer, and pesticides
- Help farmers make decisions that increase crop yields and income
- Contribute to food security by helping farmers grow crops better

---

## Proposed Solution

KrushiRakshak solves these problems by building one app that brings together different technologies and data sources. Here's how we built it:

### **System Overview**

KrushiRakshak is a web app with two main parts: a frontend built with React that users see and interact with, and a backend built with FastAPI (Python) that does the heavy work. The app connects to external sources like IMD for weather, Agmarknet for market prices, and Bhuvan for satellite images. We built a smart system called the Fusion Engine that uses rules to create helpful advice for farmers.

### **Core Components**

#### 1. **Fusion Engine (The Brain of Our System)**
The Fusion Engine is what makes KrushiRakshak smart. It does these things:
- Takes data from weather, market, satellite, and crop information and puts it together
- Uses simple rules to find problems and opportunities
- Creates specific advice for each crop type with recommendations sorted by importance
- Checks for pest risks, irrigation needs, and market problems
- Tells farmers how serious problems are and what they should do about it

#### 2. **User Dashboard**
A main screen that shows everything at once:
- Current weather (temperature, humidity, rain, wind)
- Today's market prices for crops like cotton, wheat, rice
- Important alerts and warnings
- How healthy each crop is
- Quick links to get advice and visit the community section

#### 3. **Crop Advisory System**
A system that gives personalized advice:
- Looks at conditions specific to your location and crop type
- Suggests what to do for pests, watering, and taking care of crops
- Lists actions in order of importance (do this first, then this)
- Explains why each recommendation is given
- Changes advice based on what stage your crop is in (planting, growing, flowering, etc.)

#### 4. **Community Platform**
A place where farmers can connect:
- Write posts with text and photos
- Organize posts by type (tips, questions, problems, success stories)
- Like and comment on posts
- Filter posts by crop type or region
- See what topics are popular and who's helping the most
- View profiles and see what other farmers have posted

#### 5. **AI Chatbot (AgriBot)**
A smart helper powered by Google Gemini that:
- Answers farming questions right away
- Gives advice in simple language that farmers can understand
- Works all day and night without needing humans
- Understands what farmers are asking and gives helpful answers

#### 6. **Progressive Web App (PWA) Features**
- **Works Offline**: Uses special technology to work even without internet
- **Can Be Installed**: Can be added to phones like a regular app
- **Works on All Devices**: Looks good and works well on phones, tablets, and computers
- **Loads Fast**: Stores data smartly so pages load quickly
- **Push Notifications**: (Coming soon) Will alert farmers about important updates

#### 7. **Multi-Language Support**
- Built to support multiple languages
- Currently works in English and Marathi
- Easy to add more languages in the future

### **Technical Architecture**

We built the app using modern tools that can grow as more people use it:

- **Frontend**: React 18 with TypeScript, Vite for building, Tailwind CSS for styling
- **Backend**: FastAPI (Python) with SQLAlchemy for database work
- **Database**: SQLite for testing / PostgreSQL for when we launch
- **Authentication**: JWT tokens with secure password storage
- **API Integration**: Standard REST APIs to connect to external data sources
- **State Management**: React Query for server data, React hooks for local data
- **UI Components**: shadcn/ui library for consistent, easy-to-use interface

### **Data Flow**

Here's how data moves through the system:

1. **Getting Data**: The app fetches weather from IMD, prices from Agmarknet, and satellite images from Bhuvan
2. **Processing Data**: The Fusion Engine takes all this raw data and uses rules to make sense of it
3. **Creating Advice**: The system creates personalized advice based on who the farmer is and where their farm is
4. **Showing Information**: The frontend displays everything in a way that's easy to understand
5. **User Actions**: Farmers can read advice, talk to other farmers, and ask the AI chatbot questions
6. **Offline Access**: Important data is saved so farmers can access it even without internet

### **Key Features**

- **Real-Time Weather**: Live weather updates with forecasts and warnings
- **Market Prices**: Current and past prices with trend arrows showing if prices are going up or down
- **Crop Health Check**: Uses satellite data (NDVI) to see how healthy crops are
- **Early Warnings**: Alerts farmers about pests, diseases, and bad weather before problems get serious
- **Community**: A place where farmers can share tips and help each other
- **AI Helper**: A chatbot that answers farming questions instantly
- **Works Offline**: Everything works even when there's no internet
- **Multiple Languages**: Available in different languages so more farmers can use it

### **Expected Impact**

What we hope KrushiRakshak will do:
- Help farmers grow more crops by using data to make better decisions
- Reduce crop losses by warning farmers about problems early
- Help farmers earn more money by showing them the best time to sell
- Let farmers share knowledge and learn from each other
- Make advanced farming technology available to everyone, not just tech-savvy farmers
- Help farmers use water, fertilizer, and pesticides more wisely

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER (Frontend)                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  React PWA Application (TypeScript + Vite)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   Pages      │  │ Components   │  │   Services   │           │  │
│  │  │  - Home      │  │ - Navbar     │  │ - API Client │           │  │
│  │  │  - Dashboard │  │ - ChatBot   │  │ - Auth      │           │  │
│  │  │  - Advisory  │  │ - Footer    │  │ - i18n      │           │  │
│  │  │  - Community │  │ - UI Kit     │  │             │           │  │
│  │  │  - Profile   │  │             │  │             │           │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │  │
│  │                                                                   │  │
│  │  PWA Features: Service Worker, Offline Cache, Install Prompt    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS/REST API
                                    │ (JWT Authentication)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER (Backend)                        │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application (Python)                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │   Auth       │  │   Fusion     │  │  Community   │            │  │
│  │  │   Router     │  │   Engine     │  │   Router     │            │  │
│  │  │ - Signup      │  │ - Dashboard  │  │ - Posts     │            │  │
│  │  │ - Login      │  │ - Advisory   │  │ - Comments  │            │  │
│  │  │ - Profile    │  │ - Rules      │  │ - Likes     │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  │                                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   AI         │  │   Services    │  │   Utils      │          │  │
│  │  │   Router     │  │ - Weather     │  │ - Loader     │          │  │
│  │  │ - Chat       │  │ - Market      │  │ - Geocode    │          │  │
│  │  │ (Gemini)      │  │ - NDVI        │  │             │          │  │
│  │  └──────────────┘  │ - Crop Stage │  └──────────────┘          │  │
│  │                     │ - Gov Alerts │                            │  │
│  │                     └──────────────┘                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SQLAlchemy ORM
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    Database (SQLite/PostgreSQL)                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   Users      │  │   Posts       │  │  Comments     │           │  │
│  │  │   - id       │  │   - id       │  │  - id        │           │  │
│  │  │   - email    │  │   - content  │  │  - content   │           │  │
│  │  │   - crop     │  │   - author   │  │  - post_id    │           │  │
│  │  │   - location │  │   - likes    │  │  - user_id   │           │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │  │
│  │                                                                   │  │
│  │  ┌──────────────┐                                                │  │
│  │  │  PostLikes   │                                                │  │
│  │  │  - post_id   │                                                │  │
│  │  │  - user_id   │                                                │  │
│  │  └──────────────┘                                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ External API Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │   IMD        │  │  Agmarknet   │  │   Bhuvan     │  │  Gemini  │  │
│  │   Weather    │  │  Market     │  │  Satellite  │  │  AI API  │  │
│  │   API        │  │  Prices API │  │  Imagery     │  │          │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Explanation

#### 1. **Client Layer (Frontend)**
The frontend is a web app built with React and TypeScript that works well on phones and computers.

- **Pages**: Main screens like Home, Dashboard, Advisory, Community, Profile, and login/signup pages
- **Components**: Reusable pieces like navigation bar, chatbot, footer, and a full set of UI components (shadcn/ui)
- **Services**: Code that talks to the backend API, handles login, and supports multiple languages
- **PWA Features**: Special code that makes it work offline, allows installation, and stores data efficiently

#### 2. **Application Layer (Backend)**
The backend is built with FastAPI and provides APIs organized into separate sections.

- **Auth Router**: Handles signup, login, creating tokens, and managing user profiles
- **Fusion Engine Router**: The smart part that combines all data sources and creates advice
- **Community Router**: Manages posts, comments, likes, image uploads, and user interactions
- **AI Router**: Connects to Google Gemini for the chatbot
- **Services Layer**: Separate services for weather data, market prices, NDVI processing, crop stage detection, and location services
- **Utils**: Helper functions for loading data, caching, and other common tasks

#### 3. **Data Layer**
The data layer uses SQLAlchemy to work with the database. It works with SQLite for testing and PostgreSQL for production.

- **Users Table**: Stores user accounts, profiles, and settings
- **Posts Table**: Stores community posts with content, metadata, and how many likes/comments they have
- **Comments Table**: Stores comments that users write on posts
- **PostLikes Table**: Tracks which users liked which posts

#### 4. **External Services Layer**
The system connects to several external services to get farming data.

- **IMD Weather API**: Real-time weather and forecasts from India Meteorological Department
- **Agmarknet API**: Current and past market prices for crops
- **Bhuvan Satellite**: Satellite images and NDVI data to check crop health
- **Google Gemini API**: AI chatbot that gives instant farming advice

### Data Flow Architecture

```
User Request
    │
    ▼
Frontend (React)
    │
    ├─► API Client (axios)
    │       │
    │       ├─► JWT Token (if authenticated)
    │       │
    │       ▼
    │   Backend (FastAPI)
    │       │
    │       ├─► Authentication Check
    │       │
    │       ├─► Database Query (SQLAlchemy)
    │       │       │
    │       │       ▼
    │       │   Database (SQLite/PostgreSQL)
    │       │
    │       ├─► External API Calls
    │       │       │
    │       │       ├─► Weather Service → IMD API
    │       │       ├─► Market Service → Agmarknet API
    │       │       ├─► NDVI Service → Bhuvan API
    │       │       └─► AI Service → Gemini API
    │       │
    │       ├─► Fusion Engine Processing
    │       │       │
    │       │       ├─► Rule Evaluation
    │       │       ├─► Data Combination
    │       │       └─► Advisory Generation
    │       │
    │       ▼
    │   JSON Response
    │
    ▼
Frontend Rendering
    │
    ├─► State Update (React Query)
    ├─► UI Update (React Components)
    └─► Cache Update (Service Worker)
```

### Request-Response Cycle

1. **User Interaction**: User interacts with the frontend (clicks button, submits form, etc.)
2. **API Request**: Frontend makes HTTP request via axios with optional JWT token
3. **Authentication**: Backend validates JWT token for protected endpoints
4. **Data Retrieval**: Backend queries database and/or calls external APIs
5. **Processing**: Fusion Engine processes data and generates advisories
6. **Response**: Backend returns JSON response
7. **State Update**: Frontend updates React state and re-renders UI
8. **Caching**: Service worker caches responses for offline access

---

## Technologies Used

### Frontend Technologies

#### **Core Framework & Language**
- **React 18.3.1**: Modern JavaScript library for building user interfaces
- **TypeScript 5.8.3**: Typed superset of JavaScript for enhanced code quality and developer experience
- **Vite 7.2.2**: Next-generation frontend build tool for fast development and optimized production builds

#### **UI Framework & Styling**
- **Tailwind CSS 3.4.17**: Utility-first CSS framework for rapid UI development
- **shadcn/ui**: High-quality, accessible React component library built on Radix UI primitives
- **Radix UI**: Unstyled, accessible component primitives for building design systems
- **Lucide React**: Beautiful, customizable icon library
- **next-themes**: Theme provider for dark/light mode support

#### **State Management & Data Fetching**
- **TanStack React Query 5.83.0**: Powerful data synchronization library for server state management
- **React Hooks**: Built-in React hooks (useState, useEffect, useContext) for local state management
- **Zustand** (via React Query): Lightweight state management solution

#### **Routing & Navigation**
- **React Router DOM 6.30.1**: Declarative routing for React applications

#### **Form Handling & Validation**
- **React Hook Form 7.61.1**: Performant, flexible form library with easy validation
- **Zod 3.25.76**: TypeScript-first schema validation library
- **@hookform/resolvers 3.10.0**: Validation resolver for React Hook Form

#### **HTTP Client**
- **Axios 1.13.2**: Promise-based HTTP client for making API requests

#### **Internationalization**
- **i18next 25.6.2**: Internationalization framework for JavaScript
- **react-i18next 16.3.3**: React bindings for i18next
- **i18next-browser-languagedetector 8.2.0**: Language detection plugin for i18next

#### **PWA & Offline Support**
- **vite-plugin-pwa 1.1.0**: Vite plugin for Progressive Web App features
- **Workbox Window 7.3.0**: Service worker management and lifecycle events

#### **Data Visualization**
- **Recharts 2.15.4**: Composable charting library built on React and D3

#### **Utilities**
- **date-fns 3.6.0**: Modern JavaScript date utility library
- **clsx**: Utility for constructing className strings conditionally
- **tailwind-merge**: Utility to merge Tailwind CSS classes
- **class-variance-authority**: Utility for building component variants

#### **Development Tools**
- **ESLint 9.32.0**: JavaScript/TypeScript linter for code quality
- **TypeScript ESLint 8.38.0**: TypeScript-specific linting rules
- **PostCSS 8.5.6**: CSS transformation tool
- **Autoprefixer 10.4.21**: PostCSS plugin to parse CSS and add vendor prefixes

### Backend Technologies

#### **Core Framework**
- **FastAPI 0.115.0**: Modern, fast web framework for building APIs with Python
- **Python 3.x**: Programming language for backend development
- **Uvicorn 0.30.0**: Lightning-fast ASGI server implementation

#### **Database & ORM**
- **SQLAlchemy 2.0.0**: Python SQL toolkit and Object-Relational Mapping (ORM) library
- **SQLite**: Lightweight, file-based database (development)
- **PostgreSQL** (via psycopg 3.1.18): Production-ready relational database support

#### **Authentication & Security**
- **python-jose[cryptography] 3.3.0**: JWT (JSON Web Token) implementation for authentication
- **passlib[bcrypt] 1.7.4**: Password hashing library with bcrypt support
- **python-multipart 0.0.9**: Multipart form data parsing for file uploads

#### **Data Validation & Serialization**
- **Pydantic 2.0.0**: Data validation using Python type annotations
- **email-validator 2.0.0**: Email address validation library

#### **HTTP Clients**
- **httpx 0.24.0**: Modern HTTP client for making async requests to external APIs
- **requests 2.31.0**: Simple HTTP library for synchronous API calls

#### **AI & Machine Learning**
- **google-generativeai 0.3.0**: Official Google SDK for Gemini AI models

#### **Geospatial & Satellite Data**
- **rasterio 1.3.0**: Geospatial raster I/O library for satellite imagery processing
- **pystac-client 0.7.0**: Python client for SpatioTemporal Asset Catalog (STAC) APIs
- **numpy 1.24.0**: Fundamental package for scientific computing with Python

#### **Cloud Services**
- **boto3 1.28.0**: AWS SDK for Python (for potential cloud storage integration)

#### **Utilities**
- **python-dotenv 1.0.0**: Loads environment variables from .env files
- **jinja2 3.1.0**: Template engine for generating dynamic content

### Database Technologies

- **SQLite**: File-based relational database for development and testing
- **PostgreSQL**: Production-grade relational database with full SQL support
- **SQLAlchemy ORM**: Database abstraction layer supporting multiple database backends

### External APIs & Services

- **IMD Weather API**: India Meteorological Department weather data
- **Agmarknet API**: Government of India agricultural market price data
- **Bhuvan Satellite API**: ISRO's satellite imagery and NDVI data
- **Google Gemini 2.5 Pro API**: AI-powered chatbot service
- **Open-Meteo API**: Alternative weather data source (fallback)

### Development & Build Tools

#### **Frontend Build Tools**
- **Vite**: Fast build tool and dev server
- **SWC**: Speedy Web Compiler for TypeScript/JavaScript
- **PostCSS**: CSS processing
- **Autoprefixer**: Automatic vendor prefixing

#### **Backend Development**
- **Uvicorn**: ASGI server with hot-reload support
- **Python Virtual Environment**: Isolated Python environment management

#### **Version Control & Collaboration**
- **Git**: Distributed version control system
- **GitHub**: Code hosting and collaboration platform

### Deployment & Infrastructure

- **PWA Support**: Service workers, manifest files, offline caching
- **CORS Middleware**: Cross-Origin Resource Sharing for frontend-backend communication
- **Environment Variables**: Secure configuration management via .env files
- **Docker** (potential): Containerization for consistent deployments

### Testing & Quality Assurance

- **Test Scripts**: Python-based test scripts for API endpoint testing
- **TypeScript**: Compile-time type checking for frontend
- **ESLint**: Code linting and quality checks
- **Pydantic**: Runtime data validation for backend

---

## Frontend Architecture

### Page-Wise Overview

The KrushiRakshak frontend consists of 13 main pages, each serving a specific purpose in the application workflow:

#### 1. **Home Page** (`/`)
- **Purpose**: Landing page and entry point for new users
- **Features**:
  - Hero section with call-to-action buttons
  - Feature showcase (Weather, Advisory, Community, Market)
  - Dynamic CTA based on authentication status
  - Links to dashboard, installation guide, and about page
- **State Management**: Uses `useTranslation` for i18n and `isAuthenticated()` for conditional rendering
- **Key Components**: Hero section, feature cards, CTA section

#### 2. **Dashboard Page** (`/dashboard`)
- **Purpose**: Central hub displaying real-time agricultural data and insights
- **Features**:
  - Real-time weather summary (temperature, humidity, rainfall, wind)
  - Market prices for major crops with trend indicators
  - Crop health overview with NDVI data
  - Active alerts and warnings
  - Quick advisory preview for user's crop
  - Refresh functionality
- **State Management**: 
  - `useState` for dashboard data, loading states, and errors
  - `useEffect` for data fetching on mount and user crop changes
  - Fetches from `/fusion/dashboard` and `/fusion/advisory/{crop}` endpoints
- **Key Components**: Weather cards, market price cards, alert cards, crop health indicators

#### 3. **Advisory Page** (`/advisory` or `/advisory/:crop`)
- **Purpose**: Detailed, crop-specific agricultural advisories
- **Features**:
  - Crop selector dropdown (cotton, wheat, rice, sugarcane, soybean, onion)
  - Priority and severity indicators
  - Analysis summary
  - Triggered rules breakdown
  - Prioritized recommendations with icons
  - Rule breakdown (pest, irrigation, market scores)
  - Download PDF option (future enhancement)
- **State Management**:
  - `useParams` to read crop from URL
  - `useState` for advisory data, selected crop, loading states
  - `useEffect` to fetch advisory when crop changes
  - Auto-loads user's crop if no URL parameter
- **Key Components**: Crop selector, advisory cards, recommendation list, rule breakdown

#### 4. **Community Page** (`/community`)
- **Purpose**: Social platform for farmers to share knowledge and experiences
- **Features**:
  - Post feed with text and image support
  - Create/edit/delete posts (for own posts)
  - Like and comment functionality
  - Crop and category filtering (tip, question, issue, success)
  - Search functionality
  - Top contributors sidebar
  - Trending topics display
  - Collapsible comments section
  - Image preview for post images
- **State Management**:
  - Complex state with multiple `useState` hooks:
    - Posts array, loading states, error handling
    - Post creation modal state
    - Comment state per post (using Record<number, Comment[]>)
    - Filter states (crop, category, search)
    - Top contributors and trending topics
  - `useEffect` for fetching posts, contributors, and trending topics
  - Real-time updates for likes and comments
- **Key Components**: Post cards, create post modal, comment section, filter dropdowns, search input

#### 5. **Profile Page** (`/profile`)
- **Purpose**: User profile management and settings
- **Features**:
  - View and edit user information
  - Update name, phone, crop, location details
  - GPS location detection
  - Form validation
  - Save changes to backend
- **State Management**:
  - `useState` for form data and loading states
  - `useEffect` to load user data on mount
  - Authentication check with redirect to login if not authenticated
- **Key Components**: Profile form, location detector, save button

#### 6. **User Profile Page** (`/profile/:userId`)
- **Purpose**: View another user's profile and posts
- **Features**:
  - Display user's posts
  - Like and comment on user's posts
  - View user's post history
- **State Management**:
  - `useParams` to get userId from URL
  - `useState` for posts, comments, loading states
  - `useEffect` to fetch user posts on mount
- **Key Components**: User posts list, like/comment functionality

#### 7. **Login Page** (`/login`)
- **Purpose**: User authentication
- **Features**:
  - Email and password login form
  - Form validation
  - Error handling with user-friendly messages
  - Redirect to dashboard on success
  - Link to signup page
- **State Management**:
  - `useState` for email, password, loading state
  - Form submission handler with error handling
- **Key Components**: Login form, error messages

#### 8. **Signup Page** (`/signup`)
- **Purpose**: New user registration
- **Features**:
  - Registration form (name, email, password, phone, user type)
  - GPS location detection (optional)
  - Form validation
  - Error handling
  - Redirect to dashboard on success
- **State Management**:
  - `useState` for form data, coordinates, loading states
  - Location detection handler
- **Key Components**: Signup form, location detector

#### 9. **Report Page** (`/report`)
- **Purpose**: Report agricultural issues
- **Features**:
  - Issue reporting form (crop type, issue type, severity)
  - GPS coordinates capture
  - Additional notes field
  - Photo upload (future enhancement)
  - Offline queue indicator
- **State Management**:
  - `useState` for form data and online/offline status
  - Location detection handler
- **Key Components**: Report form, location detector

#### 10. **Contact Page** (`/contact`)
- **Purpose**: Contact information and support form
- **Features**:
  - Contact information display (email, phone, address)
  - Contact form (name, email, subject, message)
  - Form submission handling
- **State Management**: Simple form state with `useState`
- **Key Components**: Contact cards, contact form

#### 11. **About Page** (`/about`)
- **Purpose**: Information about KrushiRakshak project
- **Features**:
  - Mission statement
  - Community information
  - Innovation highlights
  - Static content display
- **State Management**: No state management (static page)
- **Key Components**: Information cards

#### 12. **Install Page** (`/install`)
- **Purpose**: PWA installation guide and prompt
- **Features**:
  - Installation instructions for Android and iOS
  - Install button with browser prompt
  - PWA features explanation
  - Installation status check
- **State Management**:
  - `useState` for install prompt event and installation status
  - `useEffect` to listen for install events
- **Key Components**: Install button, feature cards, instruction cards

#### 13. **NotFound Page** (`*`)
- **Purpose**: 404 error page for invalid routes
- **Features**:
  - Error message
  - Link back to home
- **State Management**: No state management (static page)

### Component Structure

#### **Layout Components**

1. **Navbar** (`src/components/Navbar.tsx`)
   - Responsive navigation bar
   - Authentication-aware menu items
   - Language switcher (English/Marathi)
   - Theme switcher (light/dark)
   - User dropdown menu
   - Mobile hamburger menu

2. **Footer** (`src/components/Footer.tsx`)
   - Site footer with links
   - Copyright information
   - Social media links (placeholder)
   - Quick navigation links

3. **OfflineBanner** (`src/components/OfflineBanner.tsx`)
   - Detects online/offline status
   - Shows banner when connection status changes
   - Auto-hides after 3 seconds when back online
   - Uses `navigator.onLine` API

4. **InstallPrompt** (`src/components/InstallPrompt.tsx`)
   - PWA installation prompt
   - Appears after delay if not dismissed
   - Handles browser install events
   - Respects user dismissal preference (localStorage)

#### **Feature Components**

1. **ChatBot** (`src/components/ChatBot.tsx`)
   - Floating chat button
   - Expandable chat window
   - Message history display
   - Integration with AI API (`/ai/chat`)
   - Loading states during AI response
   - Error handling with user-friendly messages

#### **UI Component Library** (`src/components/ui/`)

The application uses shadcn/ui component library with 48+ pre-built components:
- Form components: Input, Textarea, Select, Checkbox, Radio, Switch
- Layout components: Card, Separator, ScrollArea, Resizable
- Navigation: Tabs, Breadcrumb, Navigation Menu
- Feedback: Alert, Toast, Dialog, Popover, Tooltip
- Data display: Table, Badge, Avatar, Progress, Skeleton
- Overlay: Sheet, Drawer, Dropdown Menu, Context Menu
- And many more...

### State Management Patterns

#### **1. Local Component State (useState)**
- Used for component-specific state (forms, UI toggles, loading states)
- Examples: form inputs, modal open/close, loading indicators

#### **2. Server State Management (React Query)**
- **TanStack React Query** is configured in `App.tsx`
- Used for:
  - Caching API responses
  - Automatic refetching
  - Background updates
  - Optimistic updates (future enhancement)
- Currently, most pages use direct `useState` + `useEffect` for API calls, but React Query infrastructure is in place

#### **3. Authentication State**
- Stored in `localStorage`:
  - `access_token`: JWT token
  - `user_data`: Serialized user object
- Helper functions in `src/services/api.ts`:
  - `isAuthenticated()`: Checks for token presence
  - `getUser()`: Retrieves user from localStorage
  - `logoutUser()`: Clears authentication data

#### **4. Global State (Context API)**
- **Theme Context**: Provided by `next-themes` for dark/light mode
- **i18n Context**: Provided by `react-i18next` for language management
- **Query Client**: Provided by React Query for server state

### Routing Configuration

Routing is configured in `src/App.tsx` using React Router DOM:

```typescript
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/login" element={<Login />} />
  <Route path="/signup" element={<Signup />} />
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/advisory/:crop" element={<Advisory />} />
  <Route path="/advisory" element={<Advisory />} />
  <Route path="/community" element={<Community />} />
  <Route path="/report" element={<Report />} />
  <Route path="/profile" element={<Profile />} />
  <Route path="/profile/:userId" element={<UserProfile />} />
  <Route path="/contact" element={<Contact />} />
  <Route path="/about" element={<About />} />
  <Route path="/install" element={<Install />} />
  <Route path="*" element={<NotFound />} />
</Routes>
```

**Route Protection**: 
- Most routes are public, but components check authentication internally
- Protected routes (Profile, UserProfile) redirect to `/login` if not authenticated
- Authentication check uses `isAuthenticated()` helper function

### API Integration

#### **API Client Setup** (`src/services/api.ts`)

1. **Axios Instance Configuration**
   - Base URL: `http://localhost:8000` (configurable via `VITE_API_URL`)
   - Default headers: `Content-Type: application/json`
   - Request interceptor: Adds JWT token to protected endpoints
   - Response interceptor: Handles 401 errors with automatic logout

2. **Request Interceptor**
   - Checks if endpoint is public (`/auth/*`, `/ai/chat`)
   - Adds `Authorization: Bearer <token>` header for protected endpoints
   - Token retrieved from `localStorage.getItem("access_token")`

3. **Response Interceptor**
   - Handles 401 (Unauthorized) errors
   - Clears authentication data
   - Redirects to login page (except on auth routes)

4. **API Functions Organized by Feature**:
   - **Authentication**: `loginUser`, `signupUser`, `getCurrentUser`, `updateProfile`, `logoutUser`
   - **Fusion Engine**: `getDashboardData`, `getAdvisory`
   - **Community**: `getCommunityPosts`, `createPost`, `updatePost`, `deletePost`, `togglePostLike`, `getPostComments`, `createComment`, `getUserPosts`, `getTopContributors`, `searchPosts`, `getTrendingTopics`
   - **AI Chatbot**: `askAI`
   - **Image Upload**: `uploadImage`
   - **Report**: `submitReport` (placeholder)

5. **Error Handling**:
   - Comprehensive error handling with user-friendly messages
   - Network error detection
   - Server error handling with status codes
   - Toast notifications for user feedback

### PWA Features

#### **1. Service Worker Registration** (`src/main.tsx`)
- Service worker registered at `/sw.js`
- Handled by `vite-plugin-pwa`
- Automatic registration on app load

#### **2. PWA Manifest** (`vite.config.ts`)
- Configured via `VitePWA` plugin
- App name: "KrushiRakshak - Smart Farming Assistant"
- Short name: "KrushiRakshak"
- Icons: 192x192 and 512x512 PNG icons
- Theme color: `#2E7D32` (green)
- Display mode: `standalone`
- Start URL: `/`

#### **3. Offline Support**
- **Service Worker Caching**:
  - Caches static assets (JS, CSS, HTML, images)
  - Caches Google Fonts with CacheFirst strategy
  - Runtime caching for API responses (via Workbox)
- **Offline Detection**:
  - `OfflineBanner` component monitors connection status
  - Uses `navigator.onLine` and `online`/`offline` events
- **Offline Functionality**:
  - Cached pages work offline
  - Cached API responses available offline
  - Form submissions can be queued (future enhancement)

#### **4. Install Prompt**
- **InstallPrompt Component**: Shows install prompt after delay
- **Install Page**: Dedicated page with installation instructions
- **Browser Events**:
  - Listens for `beforeinstallprompt` event
  - Handles `appinstalled` event
  - Respects user dismissal (stored in localStorage)

#### **5. Workbox Configuration**
- **Cache Strategies**:
  - Static assets: Precached
  - Google Fonts: CacheFirst with 1-year expiration
  - API responses: NetworkFirst (default)
- **Auto-update**: Service worker auto-updates when new version available

### Internationalization (i18n)

#### **Setup** (`src/i18n/i18n.ts`)
- Uses `i18next` and `react-i18next`
- Language detector: Checks localStorage, navigator, HTML tag
- Supported languages: English (en), Marathi (mr)
- Fallback language: English

#### **Translation Files**
- `src/i18n/locales/en.json`: English translations
- `src/i18n/locales/mr.json`: Marathi translations (placeholder structure)

#### **Usage in Components**
```typescript
import { useTranslation } from "react-i18next";

const Component = () => {
  const { t } = useTranslation();
  return <h1>{t("home.hero_title")}</h1>;
};
```

#### **Translation Keys Structure**
- Organized by feature/page: `home.*`, `dashboard.*`, `advisory.*`, `community.*`, etc.
- Nested structure for related translations
- Interpolation support: `{{variable}}` syntax

#### **Language Switcher**
- Available in Navbar component
- Switches between English and Marathi
- Preference stored in localStorage
- Updates UI immediately on language change

### Frontend Build & Development

#### **Build Tool: Vite**
- Fast development server with HMR (Hot Module Replacement)
- Optimized production builds
- Path aliases: `@/` resolves to `src/`
- Environment variables: `VITE_API_URL` for API base URL

#### **Development Server**
- Runs on `http://localhost:8080` (configurable)
- Auto-reload on file changes
- Fast refresh for React components

#### **Production Build**
- Command: `npm run build`
- Output: `dist/` directory
- Optimized and minified assets
- Service worker generated automatically

---

## Backend Architecture - Core Systems

### Authentication System

The KrushiRakshak backend implements a secure JWT-based authentication system using industry-standard practices.

#### **1. JWT Token Generation**

**Token Creation** (`auth.py`):
- Uses `python-jose` library for JWT encoding/decoding
- Algorithm: `HS256` (HMAC with SHA-256)
- Secret Key: Stored in environment variable `SECRET_KEY`
- Token Expiry: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60 minutes)
- Token Payload: Contains user email (`sub` field) and expiration time (`exp`)

**Token Structure**:
```python
{
  "sub": "user@example.com",  # Subject (user email)
  "exp": 1234567890            # Expiration timestamp
}
```

#### **2. Password Hashing**

**Implementation** (`crud.py`):
- Uses `passlib` library with `bcrypt` scheme
- Bcrypt is a secure, adaptive hashing algorithm
- Passwords are hashed before storage in database
- Plain passwords are never stored

**Password Operations**:
- **Hashing**: `pwd_context.hash(password)` - Used during user registration
- **Verification**: `pwd_context.verify(plain_password, hashed_password)` - Used during login

#### **3. OAuth2 Password Bearer Flow**

**OAuth2 Scheme** (`auth.py`):
- Uses FastAPI's `OAuth2PasswordBearer` for token extraction
- Token URL: `/auth/login`
- Token extraction: Automatically extracts token from `Authorization: Bearer <token>` header
- Dependency injection: `get_current_user` function validates token and returns user

#### **4. Authentication Endpoints**

**POST `/auth/signup`**:
- Registers a new user
- Validates email uniqueness
- Hashes password before storage
- Optionally performs reverse geocoding if GPS coordinates provided
- Returns user data (without password) and access token
- Status Code: `201 Created`

**POST `/auth/login`**:
- Authenticates user with email and password
- Verifies password against stored hash
- Generates JWT access token
- Returns token and user information
- Status Code: `200 OK` or `400 Bad Request` (invalid credentials)

**GET `/auth/me`**:
- Returns current authenticated user's details
- Requires `Authorization: Bearer <token>` header
- Validates token and extracts user email
- Status Code: `200 OK` or `401 Unauthorized`

**PATCH `/auth/profile`**:
- Updates current user's profile information
- Requires authentication
- Allows partial updates (only provided fields are updated)
- Status Code: `200 OK` or `404 Not Found`

#### **5. Authentication Flow**

```
1. User Registration:
   User → POST /auth/signup → Password Hashed → User Created → JWT Token Generated → Returned

2. User Login:
   User → POST /auth/login → Password Verified → JWT Token Generated → Returned

3. Protected Endpoint Access:
   User → Request with JWT Token → Token Validated → User Retrieved → Request Processed

4. Token Validation:
   Extract Token → Decode JWT → Verify Signature → Check Expiry → Get User from DB
```

#### **6. Security Features**

- **Password Security**: Bcrypt hashing with salt
- **Token Security**: Signed tokens prevent tampering
- **Token Expiry**: Tokens expire after configured time
- **HTTPS Recommended**: Tokens should be transmitted over HTTPS in production
- **No Password in Responses**: Passwords never returned in API responses

### Database Models

The database schema is defined using SQLAlchemy ORM models with clear relationships and constraints.

#### **1. User Model** (`models.py`)

**Table**: `users`

**Fields**:
- `id` (Integer, Primary Key): Unique user identifier
- `email` (String, Unique, Indexed, Required): User email address
- `name` (String, Optional): User's full name
- `phone` (String, Optional): User's phone number
- `user_type` (String, Optional): Type of user (farmer, advisor, etc.)
- `hashed_password` (String, Required): Bcrypt-hashed password
- `crop` (String, Optional): Primary crop the user grows
- `location` (String, Optional): Farm location (GPS coordinates or address)
- `state` (String, Optional): State/region
- `district` (String, Optional): District
- `village` (String, Optional): Village
- `is_active` (Boolean, Default: True): Account active status
- `created_at` (DateTime, Auto-generated): Account creation timestamp

**Relationships**:
- `posts`: One-to-many relationship with Post model (cascade delete)

#### **2. Post Model** (`models.py`)

**Table**: `posts`

**Fields**:
- `id` (Integer, Primary Key): Unique post identifier
- `content` (Text, Required): Post content/text
- `author_id` (Integer, Foreign Key → users.id, Required): Post author
- `region` (String, Optional): State/region of the author
- `crop` (String, Optional): Crop type mentioned in post
- `category` (String, Optional): Post category (tip, question, issue, success)
- `likes_count` (Integer, Default: 0): Number of likes
- `comments_count` (Integer, Default: 0): Number of comments
- `image_url` (String, Optional): URL to uploaded image
- `created_at` (DateTime, Auto-generated): Post creation timestamp
- `updated_at` (DateTime, Auto-updated): Last update timestamp

**Relationships**:
- `author_user`: Many-to-one relationship with User model
- `likes`: One-to-many relationship with PostLike model (cascade delete)
- `comments`: One-to-many relationship with Comment model (cascade delete)

#### **3. PostLike Model** (`models.py`)

**Table**: `post_likes`

**Fields**:
- `id` (Integer, Primary Key): Unique like identifier
- `post_id` (Integer, Foreign Key → posts.id, Required): Liked post
- `user_id` (Integer, Foreign Key → users.id, Required): User who liked
- `created_at` (DateTime, Auto-generated): Like timestamp

**Relationships**:
- `post`: Many-to-one relationship with Post model

**Purpose**: Tracks which users liked which posts (many-to-many relationship between users and posts)

#### **4. Comment Model** (`models.py`)

**Table**: `comments`

**Fields**:
- `id` (Integer, Primary Key): Unique comment identifier
- `post_id` (Integer, Foreign Key → posts.id, Required): Post being commented on
- `user_id` (Integer, Foreign Key → users.id, Required): Comment author
- `content` (Text, Required): Comment text
- `created_at` (DateTime, Auto-generated): Comment creation timestamp
- `updated_at` (DateTime, Auto-updated): Last update timestamp

**Relationships**:
- `post`: Many-to-one relationship with Post model

#### **5. Database Relationships Diagram**

```
User (1) ────────< (Many) Post
                          │
                          ├───< (Many) PostLike
                          │
                          └───< (Many) Comment
```

**Relationship Details**:
- One User can have many Posts
- One Post belongs to one User (author)
- One Post can have many PostLikes
- One PostLike belongs to one Post and one User
- One Post can have many Comments
- One Comment belongs to one Post and one User

**Cascade Behavior**:
- Deleting a User deletes all their Posts (cascade)
- Deleting a Post deletes all its Likes and Comments (cascade)

### Database Connection

#### **1. Database Configuration** (`database.py`)

**Connection String**:
- Read from environment variable `DATABASE_URL`
- Format: `postgresql+psycopg2://user:password@host:port/database`
- SQLite format (development): `sqlite:///./agrisense_dev.db`
- PostgreSQL format (production): `postgresql+psycopg2://user:pass@localhost:5432/dbname`

**Engine Creation**:
- SQLAlchemy engine created from connection string
- Supports both SQLite (development) and PostgreSQL (production)
- Automatic connection pooling

**Session Management**:
- `SessionLocal`: Session factory for database sessions
- `get_db()`: Dependency function that provides database sessions
- Automatic session cleanup after request completion
- Uses context manager pattern (yield/close)

#### **2. Database Initialization**

**Table Creation** (`main.py`):
- `Base.metadata.create_all(bind=engine)`: Creates all tables on startup
- Only creates tables if they don't exist
- Uses SQLAlchemy declarative base for table definitions

#### **3. Database Session Lifecycle**

```
Request → get_db() → Session Created → Request Processing → Session Closed
```

**Session Management**:
- One session per request
- Session automatically closed after request completion
- Prevents connection leaks
- Ensures data consistency

### CRUD Operations

CRUD (Create, Read, Update, Delete) operations are implemented in `crud.py` to separate database logic from API routes.

#### **1. User CRUD Operations**

**Read Operations**:
- `get_user_by_email(db, email)`: Retrieve user by email address
- `get_user(db, user_id)`: Retrieve user by ID

**Create Operations**:
- `create_user(db, user)`: Create new user with hashed password
  - Hashes password using bcrypt
  - Creates User model instance
  - Commits to database
  - Returns created user

**Update Operations**:
- `update_user(db, user_id, user_update)`: Update user profile
  - Retrieves user by ID
  - Updates only provided fields (partial update)
  - Commits changes
  - Returns updated user

**Authentication Operations**:
- `verify_password(plain_password, hashed_password)`: Verify password against hash
- `authenticate_user(db, email, password)`: Authenticate user credentials
  - Retrieves user by email
  - Verifies password
  - Returns user if valid, None otherwise

#### **2. CRUD Pattern**

**Separation of Concerns**:
- Database logic in `crud.py`
- API logic in router files (`auth.py`, `community.py`)
- Models in `models.py`
- Schemas in `schemas.py`

**Benefits**:
- Reusable database functions
- Easier testing
- Cleaner router code
- Centralized database operations

### API Structure

The backend API is organized using FastAPI's router system for modularity and maintainability.

#### **1. Main Application** (`main.py`)

**FastAPI App Configuration**:
- Title: "KrushiRakshak Backend API"
- Description: "Backend API for KrushiRakshak PWA — Farmer advisory and risk management system"
- Version: "1.0.0"
- Automatic API documentation at `/docs` (Swagger UI) and `/redoc`

**CORS Configuration**:
- Allows requests from frontend origins:
  - `http://localhost:8080`
  - `http://localhost:5173`
  - `http://127.0.0.1:8080`
  - `http://127.0.0.1:5173`
- Credentials allowed: `True`
- All methods and headers allowed

**Router Registration**:
```python
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(fusion_engine.router)
app.include_router(community.router)
app.include_router(ai.router)
```

#### **2. Router Organization**

**Auth Router** (`auth.py`):
- Prefix: `/auth`
- Tags: `["auth"]`
- Endpoints:
  - `POST /auth/signup`: User registration
  - `POST /auth/login`: User authentication
  - `GET /auth/me`: Get current user
  - `PATCH /auth/profile`: Update user profile

**Fusion Engine Router** (`fusion_engine.py`):
- Prefix: `/fusion`
- Tags: `["Fusion Engine"]`
- Endpoints:
  - `GET /fusion/dashboard`: Dashboard data
  - `GET /fusion/advisory/{crop}`: Crop advisory
  - `GET /fusion/health`: Health check

**Community Router** (`community.py`):
- Prefix: `/community`
- Tags: `["community"]`
- Endpoints:
  - `GET /community/posts`: Get posts
  - `POST /community/posts`: Create post
  - `GET /community/posts/{post_id}`: Get post
  - `PATCH /community/posts/{post_id}`: Update post
  - `DELETE /community/posts/{post_id}`: Delete post
  - `POST /community/posts/{post_id}/like`: Toggle like
  - `GET /community/posts/{post_id}/comments`: Get comments
  - `POST /community/posts/{post_id}/comments`: Create comment
  - `GET /community/users/{user_id}/posts`: Get user posts
  - `GET /community/top-contributors`: Get top contributors
  - `GET /community/trending-topics`: Get trending topics
  - `POST /community/upload-image`: Upload image
  - `GET /community/images/{filename}`: Get image

**AI Router** (`ai.py`):
- Prefix: `/ai`
- Tags: `["ai"]`
- Endpoints:
  - `POST /ai/chat`: Chat with AI bot

#### **3. Request/Response Validation**

**Pydantic Schemas** (`schemas.py`):
- Request validation: Validates incoming request data
- Response serialization: Formats response data
- Type safety: Ensures data types match expected format
- Automatic documentation: Generates OpenAPI schema

**Schema Types**:
- **UserCreate**: User registration data
- **UserLogin**: Login credentials
- **UserUpdate**: Profile update data
- **UserOut**: User response data (no password)
- **PostCreate**: Post creation data
- **PostUpdate**: Post update data
- **PostOut**: Post response data
- **CommentCreate**: Comment creation data
- **CommentOut**: Comment response data

#### **4. Dependency Injection**

**Database Dependency**:
- `get_db()`: Provides database session
- Automatically closes session after request
- Used in all endpoints that need database access

**Authentication Dependency**:
- `get_current_user()`: Validates JWT token and returns user
- Used in protected endpoints
- Automatically returns 401 if token invalid

**Example Usage**:
```python
@router.get("/protected")
async def protected_endpoint(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user is automatically validated User object
    # db is database session
    return {"user": current_user.email}
```

#### **5. Error Handling**

**HTTP Exceptions**:
- `HTTPException`: Standard FastAPI exception for error responses
- Status codes: 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Internal Server Error)
- Error details: User-friendly error messages

**Error Response Format**:
```json
{
  "detail": "Error message here"
}
```

#### **6. API Documentation**

**Automatic Documentation**:
- Swagger UI: Available at `/docs`
- ReDoc: Available at `/redoc`
- OpenAPI Schema: Available at `/openapi.json`

**Documentation Features**:
- Interactive API testing
- Request/response examples
- Schema definitions
- Authentication testing

---

## Backend Architecture - Feature Modules

### Fusion Engine

The Fusion Engine is the core intelligence layer of KrushiRakshak that combines multiple data sources to generate personalized crop advisories.

#### **1. Overview**

**Purpose**: 
- Integrates weather, market, and satellite data
- Applies rule-based logic to detect risks
- Generates actionable crop-specific recommendations
- Provides severity assessments and priority rankings

**Data Sources**:
- Weather: Open-Meteo API (with IMD fallback)
- Market: Agmarknet API
- Satellite: Synthetic NDVI (Bhuvan integration ready)
- Crop Metadata: Crop-specific thresholds and stage information

#### **2. Rule-Based System**

**Rule Types**:
- **Pest Rules** (`pest_rules.json`): Detects pest infestation risks
- **Irrigation Rules** (`irrigation_rules.json`): Identifies irrigation needs
- **Market Rules** (`market_rules.json`): Analyzes market price risks

**Rule Structure**:
```json
{
  "rule_name": {
    "description": "Human-readable description",
    "conditions": [
      {"feature": "temperature", "op": ">", "value": 32},
      {"feature": "humidity", "op": ">", "value": 70}
    ],
    "score": 0.85,
    "recommendation": "Actionable advice",
    "severity": "high"
  }
}
```

**Rule Operators**:
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal
- `<=`: Less than or equal
- `==`: Equal to
- `!=`: Not equal to
- `abs_gte`: Absolute value greater than or equal

**Rule Evaluation**:
- Rules are evaluated against feature data (temperature, humidity, NDVI, etc.)
- All conditions must match for a rule to fire
- Multiple rules can fire simultaneously
- Maximum score determines overall severity

#### **3. Advisory Generation Process**

**Step 1: Data Collection**
```
User Request → Resolve Location → Fetch Weather → Fetch Market → Fetch NDVI
```

**Step 2: Feature Combination**
- Combines weather, market, and crop health data
- Adds NDVI values and changes
- Includes crop stage detection
- Merges user context (location, district, etc.)

**Step 3: Rule Evaluation**
- Evaluates pest rules against features
- Evaluates irrigation rules
- Evaluates market rules
- Calculates scores for each category

**Step 4: Advisory Assembly**
- Determines overall severity (high/medium/low)
- Generates summary
- Creates alerts list
- Builds recommendations with priorities
- Calculates rule breakdown scores

**Step 5: Response Formatting**
- Structures response with all advisory components
- Includes data source attribution
- Adds timestamps and metadata

#### **4. Fusion Engine Endpoints**

**GET `/fusion/dashboard`**:
- Returns combined dashboard data
- Includes weather, market prices, alerts, crop health
- Optional crop filter for personalized view
- Status Code: `200 OK`

**GET `/fusion/advisory/{crop}`**:
- Generates crop-specific advisory
- Combines all data sources
- Applies rule-based analysis
- Returns prioritized recommendations
- Status Code: `200 OK`

**GET `/fusion/health`**:
- Health check endpoint
- Returns service status
- Lists data sources
- Status Code: `200 OK`

#### **5. Advisory Response Structure**

```json
{
  "crop": "Cotton",
  "analysis": "High risk detected",
  "priority": "high",
  "severity": "high",
  "rule_score": 0.9,
  "fired_rules": ["High humidity + NDVI drop indicates aphid infestation risk"],
  "recommendations": [
    {
      "title": "Pest Management",
      "description": "Spray neem oil (2%) early morning",
      "priority": "high",
      "timeline": "immediate"
    }
  ],
  "rule_breakdown": {
    "pest": {"fired": [...], "score": 0.9},
    "irrigation": {"fired": [...], "score": 0.3},
    "market": {"fired": [...], "score": 0.1}
  },
  "metrics": {
    "ndvi": 0.65,
    "temperature": 32.5,
    "humidity": 75,
    "market_price": 5500
  },
  "data_sources": {
    "weather": "Open-Meteo",
    "satellite": "Bhuvan",
    "market": "Agmarknet"
  }
}
```

### Community System

The Community module provides a social platform for farmers to share knowledge, ask questions, and interact with each other.

#### **1. Post Management**

**Post Creation**:
- Users can create posts with text content
- Optional image upload support
- Crop and category tagging (tip, question, issue, success)
- Region auto-populated from user profile

**Post Retrieval**:
- Pagination support (skip/limit)
- Filtering by crop and category
- Sorting by creation date (newest first)
- Includes author information and engagement metrics

**Post Updates**:
- Authors can edit their own posts
- Updates content, crop, category, or image
- Maintains engagement counts

**Post Deletion**:
- Authors can delete their own posts
- Cascade deletion of likes and comments
- Maintains data integrity

#### **2. Like System**

**Toggle Like**:
- Users can like/unlike posts
- Prevents duplicate likes
- Updates post `likes_count` automatically
- Returns current like status

**Like Tracking**:
- `PostLike` model tracks user-post relationships
- Enables "is_liked" status in responses
- Supports like count aggregation

#### **3. Comment System**

**Comment Creation**:
- Users can comment on posts
- Text content required
- Updates post `comments_count` automatically
- Includes author information

**Comment Retrieval**:
- Fetches all comments for a post
- Includes author names
- Sorted by creation date (oldest first)
- Supports pagination

#### **4. Image Upload**

**Upload Process**:
- Accepts image files (JPG, JPEG, PNG, GIF, WEBP)
- Generates unique filenames (UUID)
- Stores in `backend/uploads/` directory
- Returns image URL for post attachment

**Image Retrieval**:
- Serves images via `/community/images/{filename}`
- Validates file existence
- Returns appropriate content type

#### **5. Advanced Features**

**Top Contributors**:
- Calculates users with most posts
- Returns top N contributors
- Includes post count
- Used for community leaderboard

**Trending Topics**:
- Extracts trending tags from posts
- Counts tag occurrences
- Returns top N trending topics
- Updates dynamically

**User Posts**:
- Retrieves all posts by a specific user
- Supports user profile pages
- Includes engagement metrics

**Search Functionality**:
- Searches post content
- Case-insensitive matching
- Returns matching posts with full details

#### **6. Community Endpoints**

**Posts**:
- `GET /community/posts`: Get posts (with filters)
- `POST /community/posts`: Create post
- `GET /community/posts/{post_id}`: Get single post
- `PATCH /community/posts/{post_id}`: Update post
- `DELETE /community/posts/{post_id}`: Delete post

**Likes**:
- `POST /community/posts/{post_id}/like`: Toggle like

**Comments**:
- `GET /community/posts/{post_id}/comments`: Get comments
- `POST /community/posts/{post_id}/comments`: Create comment

**Users**:
- `GET /community/users/{user_id}/posts`: Get user posts

**Analytics**:
- `GET /community/top-contributors`: Get top contributors
- `GET /community/trending-topics`: Get trending topics

**Images**:
- `POST /community/upload-image`: Upload image
- `GET /community/images/{filename}`: Get image

### AI Chatbot

The AI Chatbot module integrates Google Gemini 2.5 Pro to provide instant agricultural advice.

#### **1. Integration**

**Model**: Google Gemini 2.5 Pro
- Advanced language model for agricultural queries
- Context-aware responses
- Farmer-friendly language

**System Prompt**:
```
"You are AgriBot, an agriculture expert who gives simple, accurate, farmer-friendly advice."
```

**Configuration**:
- Temperature: 0.7 (balanced creativity/accuracy)
- Max Output Tokens: 500 (concise responses)
- System instruction embedded in model initialization

#### **2. Chat Endpoint**

**POST `/ai/chat`**:
- Public endpoint (no authentication required)
- Accepts user message
- Returns AI-generated reply
- Error handling for API failures

**Request Format**:
```json
{
  "message": "What is the best time to plant rice?"
}
```

**Response Format**:
```json
{
  "reply": "The best time to plant rice depends on your region..."
}
```

#### **3. Error Handling**

- Handles API failures gracefully
- Returns user-friendly error messages
- Logs errors for debugging
- Prevents frontend crashes

### Services Layer

The services layer provides modular, reusable functions for external API integration and data processing.

#### **1. Weather Service** (`services/weather.py`)

**Function**: `get_realtime_weather(lat, lon)`

**Data Source**: Open-Meteo API
- Real-time weather forecasts
- Hourly data for current conditions
- Fallback to local JSON file if API fails

**Returns**:
- Temperature (°C)
- Humidity (%)
- Rainfall (mm)
- Wind Speed (km/h)
- Timestamp and location

**Features**:
- Automatic fallback on API failure
- Timeout handling (10 seconds)
- Current hour data extraction

#### **2. Market Service** (`services/market_service.py`)

**Function**: `fetch_market_price(crop, district)`

**Data Source**: Agmarknet API (Government of India)
- Real-time market prices
- District-specific pricing
- Price trend calculation

**Returns**:
- Current price (₹/quintal)
- Market name
- Price change percentage
- Trend (up/down/stable)

**Features**:
- Crop name normalization
- District filtering
- Trend calculation from historical data
- Fallback to local JSON on API failure

#### **3. NDVI Service** (`services/ndvi_synthetic.py`)

**Functions**:
- `synthetic_ndvi(lat, lon, crop)`: Generate current NDVI
- `synthetic_ndvi_history(lat, lon, crop, days)`: Generate historical NDVI

**Purpose**: 
- Provides synthetic NDVI data for development
- Realistic seasonal patterns
- Crop-specific ranges
- Location-based variation

**NDVI Ranges by Crop**:
- Cotton: 0.35 - 0.80
- Wheat: 0.45 - 0.85
- Rice: 0.40 - 0.90
- Sugarcane: 0.50 - 0.90

**Features**:
- Seasonal cycle simulation
- Historical data generation
- Crop-specific modeling

#### **4. NDVI Utilities** (`services/ndvi_utils.py`)

**Functions**:
- `ndvi_stress_level(crop_meta, ndvi)`: Determine crop stress
- `compute_ndvi_change(current, previous)`: Calculate NDVI change

**Stress Levels**:
- Good: NDVI above threshold
- Moderate: NDVI near threshold
- Poor: NDVI below threshold

#### **5. Geocoding Service** (`services/geocode.py`)

**Function**: `reverse_geocode(lat, lon)`

**Data Source**: Nominatim (OpenStreetMap)
- Reverse geocoding from coordinates
- Extracts location information

**Returns**:
- State
- District
- Village

**Features**:
- Timeout handling
- Error handling with fallback
- User-Agent header for API compliance

#### **6. Crop Stage Service** (`services/crop_stage.py`)

**Function**: `detect_crop_stage(crop_meta, days_since_sowing)`

**Purpose**:
- Determines current crop growth stage
- Based on days since sowing
- Uses crop metadata stage ranges

**Stages**:
- Sowing
- Germination
- Vegetative
- Flowering
- Fruiting
- Maturity

#### **7. Government Alerts Service** (`services/gov_alerts.py`)

**Purpose**:
- Fetches government agricultural alerts
- Integrates with government APIs
- Provides official advisories

**Status**: Placeholder for future implementation

### Data Sources

#### **1. Weather Data**

**Primary Source**: Open-Meteo API
- URL: `https://api.open-meteo.com/v1/forecast`
- Free, no authentication required
- Global coverage
- Hourly forecasts

**Fallback**: Local JSON file
- `backend/data/weather_data.json`
- Used when API unavailable
- Ensures system reliability

**Data Fields**:
- Temperature (2m above ground)
- Relative Humidity (2m)
- Precipitation
- Wind Speed (10m)

#### **2. Market Data**

**Primary Source**: Agmarknet API
- URL: `https://api.data.gov.in/resource/...`
- Government of India data
- Public API key
- Real-time market prices

**Fallback**: Local JSON file
- `backend/data/market_prices.json`
- Historical price data
- Trend information

**Data Fields**:
- Commodity name
- Market name
- Modal price
- District
- Arrival date

#### **3. Satellite Data**

**Source**: Bhuvan (ISRO)
- Indian Space Research Organisation
- Satellite imagery
- NDVI data
- Currently using synthetic data for development

**Future Integration**:
- Direct Bhuvan API integration
- Real NDVI data
- Historical satellite imagery
- Crop health monitoring

#### **4. Geocoding Data**

**Source**: Nominatim (OpenStreetMap)
- Free reverse geocoding service
- No authentication required
- Global coverage
- Address details

### Data Processing Pipeline

#### **1. Feature Combination** (`etl/make_features.py`)

**Function**: `combine_features(weather, crop_health, market)`

**Purpose**:
- Merges data from multiple sources
- Normalizes field names
- Creates unified feature set
- Handles missing data

**Output**: Dictionary with all features for rule evaluation

#### **2. Rule Loading** (`etl/make_features.py`)

**Function**: `load_rules(rule_type)`

**Purpose**:
- Loads rules from JSON files
- Caches rules in memory
- Supports multiple rule types
- Error handling for missing files

#### **3. Rule Evaluation** (`etl/make_features.py`)

**Function**: `evaluate_rules(rules, features)`

**Purpose**:
- Evaluates rules against features
- Returns fired rules and scores
- Supports multiple operators
- Handles missing features

---

## Database Schema & ER Diagram

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│       users          │
├──────────────────────┤
│ PK  id (INTEGER)     │◄──────┐
│     email (STRING)   │       │
│     name (STRING)    │       │
│     phone (STRING)   │       │
│     user_type        │       │
│     hashed_password  │       │
│     crop (STRING)    │       │
│     location         │       │
│     state            │       │
│     district         │       │
│     village          │       │
│     is_active (BOOL) │       │
│     created_at       │       │
└──────────────────────┘       │
         │                     │
         │ 1                    │
         │                      │
         │ has many             │
         │                      │
         ▼                      │
┌──────────────────────┐       │
│       posts           │       │
├──────────────────────┤       │
│ PK  id (INTEGER)      │       │
│ FK  author_id ────────┼───────┘
│     content (TEXT)    │
│     region (STRING)   │
│     crop (STRING)     │
│     category          │
│     likes_count       │
│     comments_count    │
│     image_url         │
│     created_at        │
│     updated_at        │
└──────────────────────┘
         │
         │ 1
         │
         │ has many
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌──────────────────────┐  ┌──────────────────────┐
│    post_likes        │  │      comments        │
├──────────────────────┤  ├──────────────────────┤
│ PK  id (INTEGER)     │  │ PK  id (INTEGER)     │
│ FK  post_id ─────────┼──┤ FK  post_id ─────────┼──┐
│ FK  user_id ─────────┼──┼──┐  FK  user_id ──────┼──┼──┐
│     created_at       │  │  │  │  content (TEXT) │  │  │
└──────────────────────┘  │  │  │  │  created_at    │  │  │
                          │  │  │  │  updated_at    │  │  │
                          │  │  │  └────────────────┘  │  │
                          │  │  │                      │  │
                          │  │  │                      │  │
                          │  │  └──────────────────────┘  │
                          │  │                           │
                          │  └───────────────────────────┘
                          │
                          │ References users.id
                          │
                          └──────────────────────────────┘
```

### Relationship Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Posts | One-to-Many | One user can create many posts |
| Post → User | Many-to-One | Each post belongs to one user (author) |
| Post → PostLikes | One-to-Many | One post can have many likes |
| PostLike → Post | Many-to-One | Each like belongs to one post |
| PostLike → User | Many-to-One | Each like belongs to one user |
| Post → Comments | One-to-Many | One post can have many comments |
| Comment → Post | Many-to-One | Each comment belongs to one post |
| Comment → User | Many-to-One | Each comment belongs to one user |

### Database Tables

#### **1. users**

**Description**: Stores user account information, authentication data, and profile details.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, NOT NULL, AUTO INCREMENT | Unique user identifier |
| `email` | VARCHAR | UNIQUE, NOT NULL, INDEXED | User email address (used for login) |
| `name` | VARCHAR | NULLABLE | User's full name |
| `phone` | VARCHAR | NULLABLE | User's phone number |
| `user_type` | VARCHAR | NULLABLE | Type of user (farmer, advisor, etc.) |
| `hashed_password` | VARCHAR | NOT NULL | Bcrypt-hashed password |
| `crop` | VARCHAR | NULLABLE | Primary crop grown by user |
| `location` | VARCHAR | NULLABLE | Farm location (GPS coordinates or address) |
| `state` | VARCHAR | NULLABLE | State/region |
| `district` | VARCHAR | NULLABLE | District |
| `village` | VARCHAR | NULLABLE | Village |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Indexes**:
- Primary Key: `id`
- Unique Index: `email`
- Index: `email` (for fast lookups)

**Relationships**:
- One-to-Many with `posts` (via `author_id`)
- Cascade delete: Deleting a user deletes all their posts

**Sample Data**:
```sql
INSERT INTO users (email, name, hashed_password, crop, location, state) 
VALUES ('farmer@example.com', 'John Doe', '$2b$12$...', 'cotton', '20.5,78.3', 'Maharashtra');
```

#### **2. posts**

**Description**: Stores community posts created by users, including content, metadata, and engagement metrics.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, NOT NULL, AUTO INCREMENT | Unique post identifier |
| `content` | TEXT | NOT NULL | Post text content |
| `author_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | Post author (user ID) |
| `region` | VARCHAR | NULLABLE | State/region of the author |
| `crop` | VARCHAR | NULLABLE, INDEXED | Crop type mentioned in post |
| `category` | VARCHAR | NULLABLE, INDEXED | Post category (tip, question, issue, success) |
| `likes_count` | INTEGER | DEFAULT 0 | Number of likes (denormalized for performance) |
| `comments_count` | INTEGER | DEFAULT 0 | Number of comments (denormalized) |
| `image_url` | VARCHAR | NULLABLE | URL to uploaded image |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Post creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
- Primary Key: `id`
- Foreign Key Index: `author_id`
- Index: `crop` (for filtering)
- Index: `category` (for filtering)
- Index: `created_at` (for sorting)

**Relationships**:
- Many-to-One with `users` (via `author_id`)
- One-to-Many with `post_likes` (via `post_id`)
- One-to-Many with `comments` (via `post_id`)
- Cascade delete: Deleting a post deletes all its likes and comments

**Sample Data**:
```sql
INSERT INTO posts (content, author_id, crop, category, region) 
VALUES ('Great tip for cotton farming!', 1, 'cotton', 'tip', 'Maharashtra');
```

#### **3. post_likes**

**Description**: Junction table tracking which users liked which posts (many-to-many relationship).

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, NOT NULL, AUTO INCREMENT | Unique like identifier |
| `post_id` | INTEGER | FOREIGN KEY → posts.id, NOT NULL | Liked post |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who liked |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Like timestamp |

**Indexes**:
- Primary Key: `id`
- Foreign Key Index: `post_id`
- Foreign Key Index: `user_id`
- Composite Index: `(post_id, user_id)` (should be unique to prevent duplicate likes)

**Relationships**:
- Many-to-One with `posts` (via `post_id`)
- Many-to-One with `users` (via `user_id`)

**Constraints**:
- Unique constraint on `(post_id, user_id)` prevents duplicate likes (should be enforced)

**Sample Data**:
```sql
INSERT INTO post_likes (post_id, user_id) 
VALUES (1, 2);
```

#### **4. comments**

**Description**: Stores user comments on posts.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, NOT NULL, AUTO INCREMENT | Unique comment identifier |
| `post_id` | INTEGER | FOREIGN KEY → posts.id, NOT NULL | Post being commented on |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | Comment author |
| `content` | TEXT | NOT NULL | Comment text |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Comment creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
- Primary Key: `id`
- Foreign Key Index: `post_id`
- Foreign Key Index: `user_id`
- Index: `created_at` (for sorting)

**Relationships**:
- Many-to-One with `posts` (via `post_id`)
- Many-to-One with `users` (via `user_id`)

**Sample Data**:
```sql
INSERT INTO comments (post_id, user_id, content) 
VALUES (1, 3, 'This is very helpful!');
```

### Foreign Key Relationships

| Foreign Key | References | On Delete | On Update | Purpose |
|-------------|------------|-----------|-----------|---------|
| `posts.author_id` | `users.id` | CASCADE | CASCADE | Links post to author |
| `post_likes.post_id` | `posts.id` | CASCADE | CASCADE | Links like to post |
| `post_likes.user_id` | `users.id` | CASCADE | CASCADE | Links like to user |
| `comments.post_id` | `posts.id` | CASCADE | CASCADE | Links comment to post |
| `comments.user_id` | `users.id` | CASCADE | CASCADE | Links comment to user |

**Cascade Behavior**:
- Deleting a user deletes all their posts
- Deleting a post deletes all its likes and comments
- This maintains referential integrity

### Indexes and Performance

#### **Primary Indexes** (Automatic)
- `users.id` (Primary Key)
- `posts.id` (Primary Key)
- `post_likes.id` (Primary Key)
- `comments.id` (Primary Key)

#### **Unique Indexes**
- `users.email` (Unique constraint)

#### **Foreign Key Indexes** (Automatic)
- `posts.author_id` (Foreign Key to users.id)
- `post_likes.post_id` (Foreign Key to posts.id)
- `post_likes.user_id` (Foreign Key to users.id)
- `comments.post_id` (Foreign Key to posts.id)
- `comments.user_id` (Foreign Key to users.id)

#### **Performance Indexes** (Manual)
- `posts.crop` (For filtering posts by crop)
- `posts.category` (For filtering posts by category)
- `posts.created_at` (For sorting by date)

#### **Recommended Additional Indexes**

For better query performance, consider adding:

```sql
-- Composite index for post filtering
CREATE INDEX idx_posts_crop_category ON posts(crop, category);

-- Index for user posts query
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);

-- Unique constraint to prevent duplicate likes
CREATE UNIQUE INDEX idx_post_likes_unique ON post_likes(post_id, user_id);

-- Index for comment queries
CREATE INDEX idx_comments_post_created ON comments(post_id, created_at);
```

### Data Types and Constraints

#### **String Types**
- `VARCHAR`: Variable-length strings (no explicit length limit in SQLAlchemy)
- `TEXT`: Large text fields for post content and comments

#### **Numeric Types**
- `INTEGER`: Whole numbers for IDs and counts
- `BOOLEAN`: True/false values

#### **Date/Time Types**
- `TIMESTAMP WITH TIME ZONE`: Timezone-aware timestamps
- Auto-generated: `created_at` uses `func.now()`
- Auto-updated: `updated_at` uses `onupdate=func.now()`

#### **Constraints**
- **NOT NULL**: Required fields (id, email, hashed_password, content, etc.)
- **UNIQUE**: Email must be unique
- **DEFAULT**: Default values (is_active=True, likes_count=0, comments_count=0)
- **FOREIGN KEY**: Referential integrity constraints
- **CASCADE**: Automatic deletion of related records

### Database Statistics

**Total Tables**: 4
- `users`: 1 table
- `posts`: 1 table
- `post_likes`: 1 table
- `comments`: 1 table

**Total Relationships**: 7
- 1 One-to-Many (User → Posts)
- 4 Many-to-One (Post → User, PostLike → Post, PostLike → User, Comment → Post, Comment → User)
- 2 One-to-Many (Post → PostLikes, Post → Comments)

**Total Indexes**: 10+
- 4 Primary Keys
- 1 Unique Index
- 5+ Foreign Key Indexes
- 3+ Performance Indexes

### Sample Queries

#### **Get User with Posts**
```sql
SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.author_id
WHERE u.id = 1
GROUP BY u.id;
```

#### **Get Post with Author and Engagement**
```sql
SELECT 
    p.*,
    u.name as author_name,
    u.email as author_email,
    COUNT(DISTINCT pl.id) as total_likes,
    COUNT(DISTINCT c.id) as total_comments
FROM posts p
JOIN users u ON p.author_id = u.id
LEFT JOIN post_likes pl ON p.id = pl.post_id
LEFT JOIN comments c ON p.id = c.post_id
WHERE p.id = 1
GROUP BY p.id, u.id;
```

#### **Get Top Contributors**
```sql
SELECT 
    u.id,
    u.name,
    COUNT(p.id) as posts_count
FROM users u
JOIN posts p ON u.id = p.author_id
GROUP BY u.id, u.name
ORDER BY posts_count DESC
LIMIT 10;
```

#### **Get Posts with Like Status for User**
```sql
SELECT 
    p.*,
    CASE WHEN pl.id IS NOT NULL THEN true ELSE false END as is_liked
FROM posts p
LEFT JOIN post_likes pl ON p.id = pl.post_id AND pl.user_id = 1
ORDER BY p.created_at DESC;
```

### Database Migration History

**Initial Schema**: Created by SQLAlchemy `Base.metadata.create_all()`

**Migration 1**: Add crop and location to users
- Added `crop` column to `users` table
- Added `location` column to `users` table

**Migration 2**: Add crop and category to posts
- Added `crop` column to `posts` table
- Added `category` column to `posts` table
- Created index on `posts.crop`
- Created index on `posts.category`

### Database Design Principles

1. **Normalization**: Tables are normalized to 3NF (Third Normal Form)
2. **Referential Integrity**: Foreign keys ensure data consistency
3. **Cascade Deletes**: Maintains data integrity when deleting parent records
4. **Denormalization**: `likes_count` and `comments_count` are denormalized for performance
5. **Indexing Strategy**: Indexes on frequently queried columns
6. **Soft Deletes**: `is_active` flag allows soft deletion of users
7. **Audit Trail**: `created_at` and `updated_at` timestamps track record lifecycle

---

## API Endpoints Documentation

### Base URL

All API endpoints are prefixed with the base URL:
- **Development**: `http://localhost:8000`
- **Production**: Configure via environment variable

### Authentication

Most endpoints require JWT authentication. Include the token in the request header:
```
Authorization: Bearer <access_token>
```

**Public Endpoints** (No authentication required):
- `POST /auth/signup`
- `POST /auth/login`
- `POST /ai/chat`

**Protected Endpoints** (Authentication required):
- All other endpoints require a valid JWT token

### Response Format

**Success Response**: JSON object with requested data

**Error Response**: JSON object with error details
```json
{
  "detail": "Error message here"
}
```

### Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion (no response body)
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Authentication Endpoints

**Base Path**: `/auth`

### 1. POST `/auth/signup`

**Description**: Register a new user account.

**Authentication**: Not required (Public endpoint)

**Request Body**:
```json
{
  "email": "farmer@example.com",
  "password": "securepassword123",
  "name": "John Doe",
  "phone": "+91 9876543210",
  "userType": "farmer",
  "crop": "cotton",
  "location": "20.5,78.3",
  "latitude": 20.5,
  "longitude": 78.3,
  "state": "Maharashtra",
  "district": "Nashik",
  "village": "Village Name"
}
```

**Required Fields**: `email`, `password`, `userType`

**Optional Fields**: `name`, `phone`, `crop`, `location`, `latitude`, `longitude`, `state`, `district`, `village`

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "farmer@example.com",
  "name": "John Doe",
  "phone": "+91 9876543210",
  "userType": "farmer",
  "crop": "cotton",
  "location": "20.5,78.3",
  "state": "Maharashtra",
  "district": "Nashik",
  "village": "Village Name",
  "is_active": true
}
```

**Error Responses**:
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Validation error

---

### 2. POST `/auth/login`

**Description**: Authenticate user and receive JWT access token.

**Authentication**: Not required (Public endpoint)

**Request Body**:
```json
{
  "email": "farmer@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "farmer@example.com",
    "name": "John Doe",
    "phone": "+91 9876543210",
    "userType": "farmer",
    "crop": "cotton",
    "location": "20.5,78.3",
    "state": "Maharashtra",
    "district": "Nashik",
    "village": "Village Name",
    "is_active": true
  }
}
```

**Error Responses**:
- `400 Bad Request`: Incorrect email or password
- `422 Unprocessable Entity`: Validation error

---

### 3. GET `/auth/me`

**Description**: Get current authenticated user's details.

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "farmer@example.com",
  "name": "John Doe",
  "phone": "+91 9876543210",
  "userType": "farmer",
  "crop": "cotton",
  "location": "20.5,78.3",
  "state": "Maharashtra",
  "district": "Nashik",
  "village": "Village Name",
  "is_active": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

---

### 4. PATCH `/auth/profile`

**Description**: Update current user's profile information.

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body** (all fields optional):
```json
{
  "name": "John Updated",
  "phone": "+91 9876543211",
  "crop": "wheat",
  "location": "21.0,79.0",
  "state": "Maharashtra",
  "district": "Pune",
  "village": "New Village"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "farmer@example.com",
  "name": "John Updated",
  "phone": "+91 9876543211",
  "userType": "farmer",
  "crop": "wheat",
  "location": "21.0,79.0",
  "state": "Maharashtra",
  "district": "Pune",
  "village": "New Village",
  "is_active": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found

---

## Fusion Engine Endpoints

**Base Path**: `/fusion`

### 1. GET `/fusion/dashboard`

**Description**: Get combined dashboard data including weather, market prices, alerts, and crop health.

**Authentication**: Not required (Public endpoint)

**Query Parameters**:
- `crop` (optional, string): Filter by crop type
- `location` (optional, string): GPS coordinates "lat,lon"
- `latitude` (optional, float): Latitude
- `longitude` (optional, float): Longitude
- `state` (optional, string): State name
- `district` (optional, string): District name
- `village` (optional, string): Village name

**Example Request**:
```
GET /fusion/dashboard?crop=cotton&latitude=20.5&longitude=78.3
```

**Response** (200 OK):
```json
{
  "weather": {
    "temperature": 32.5,
    "humidity": 75,
    "rainfall": 12.5,
    "wind_speed": 8.2,
    "timestamp": "2024-01-15T10:30:00Z",
    "location": "20.5,78.3"
  },
  "market": {
    "cotton": {
      "price": 5500,
      "unit": "₹/quintal",
      "market": "Nashik",
      "price_change_percent": 2.5,
      "trend": "up"
    }
  },
  "alerts": [
    {
      "type": "pest",
      "level": "high",
      "message": "High humidity + NDVI drop indicates aphid infestation risk",
      "crop": "cotton"
    }
  ],
  "crop_health": {
    "cotton": {
      "ndvi": 0.65,
      "status": "good",
      "stage": "flowering"
    }
  },
  "ndvi": {
    "latest": 0.65,
    "change": -0.05,
    "history": [
      {"date": "2024-01-08", "ndvi": 0.70},
      {"date": "2024-01-15", "ndvi": 0.65}
    ]
  },
  "summary": {
    "total_alerts": 3,
    "high_priority_count": 1,
    "crops_monitored": 3
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "user_crop": "cotton",
  "user_district": "Nashik",
  "coordinates": {
    "latitude": 20.5,
    "longitude": 78.3
  }
}
```

**Error Responses**:
- `500 Internal Server Error`: Error loading dashboard data

---

### 2. GET `/fusion/advisory/{crop_name}`

**Description**: Get crop-specific advisory with recommendations and risk analysis.

**Authentication**: Not required (Public endpoint)

**Path Parameters**:
- `crop_name` (required, string): Crop name (e.g., "cotton", "wheat", "rice")

**Query Parameters**:
- `location` (optional, string): GPS coordinates "lat,lon"
- `latitude` (optional, float): Latitude
- `longitude` (optional, float): Longitude
- `state` (optional, string): State name
- `district` (optional, string): District name
- `village` (optional, string): Village name

**Example Request**:
```
GET /fusion/advisory/cotton?latitude=20.5&longitude=78.3&district=Nashik
```

**Response** (200 OK):
```json
{
  "crop": "Cotton",
  "analysis": "High risk detected",
  "priority": "High",
  "severity": "high",
  "rule_score": 0.9,
  "fired_rules": [
    "High humidity + NDVI drop indicates aphid infestation risk",
    "NDVI drop + flowering stage indicates bollworm risk"
  ],
  "recommendations": [
    {
      "title": "Pest Management",
      "description": "Spray neem oil (2%) early morning. Inspect underside of leaves.",
      "priority": "high",
      "timeline": "immediate"
    },
    {
      "title": "Irrigation",
      "description": "Maintain adequate soil moisture",
      "priority": "medium",
      "timeline": "within 3 days"
    }
  ],
  "rule_breakdown": {
    "pest": {
      "fired": ["High humidity + NDVI drop indicates aphid infestation risk"],
      "score": 0.9
    },
    "irrigation": {
      "fired": [],
      "score": 0.3
    },
    "market": {
      "fired": [],
      "score": 0.1
    }
  },
  "summary": "High risk detected",
  "alerts": [
    {
      "type": "pest",
      "message": "High humidity + NDVI drop indicates aphid infestation risk"
    }
  ],
  "metrics": {
    "ndvi": 0.65,
    "ndvi_change": -0.05,
    "soil_moisture": 0.6,
    "market_price": 5500,
    "temperature": 32.5,
    "humidity": 75,
    "rainfall": 12.5
  },
  "data_sources": {
    "weather": "Open-Meteo",
    "satellite": "Bhuvan",
    "market": "Agmarknet"
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Error Responses**:
- `500 Internal Server Error`: Error generating advisory

---

### 3. GET `/fusion/health`

**Description**: Health check endpoint for the Fusion Engine.

**Authentication**: Not required (Public endpoint)

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "Fusion Engine",
  "data_sources": ["IMD Weather", "Bhuvan Satellite", "Agmarknet Market"]
}
```

---

## Community Endpoints

**Base Path**: `/community`

### 1. GET `/community/posts`

**Description**: Get all posts with filtering and pagination support.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `skip` (optional, integer, default: 0): Number of posts to skip (pagination)
- `limit` (optional, integer, default: 50): Maximum number of posts to return
- `crop` (optional, string): Filter by crop type
- `category` (optional, string): Filter by category (tip, question, issue, success)

**Example Request**:
```
GET /community/posts?crop=cotton&category=tip&skip=0&limit=20
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "content": "Great tip for cotton farming!",
    "author_id": 1,
    "author": {
      "id": 1,
      "name": "John Doe",
      "email": "farmer@example.com"
    },
    "author_name": "John Doe",
    "region": "Maharashtra",
    "crop": "cotton",
    "category": "tip",
    "likes_count": 5,
    "comments_count": 2,
    "image_url": "/community/images/abc123.jpg",
    "created_at": "2024-01-15T10:30:00Z",
    "is_liked": true
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error fetching posts

---

### 2. POST `/community/posts`

**Description**: Create a new community post.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "content": "Great tip for cotton farming!",
  "region": "Maharashtra",
  "crop": "cotton",
  "category": "tip",
  "image_url": "/community/images/abc123.jpg"
}
```

**Required Fields**: `content`

**Optional Fields**: `region`, `crop`, `category`, `image_url`

**Response** (201 Created):
```json
{
  "id": 1,
  "content": "Great tip for cotton farming!",
  "author_id": 1,
  "author": {
    "id": 1,
    "name": "John Doe",
    "email": "farmer@example.com"
  },
  "author_name": "John Doe",
  "region": "Maharashtra",
  "crop": "cotton",
  "category": "tip",
  "likes_count": 0,
  "comments_count": 0,
  "image_url": "/community/images/abc123.jpg",
  "created_at": "2024-01-15T10:30:00Z",
  "is_liked": false
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `422 Unprocessable Entity`: Validation error

---

### 3. GET `/community/posts/{post_id}`

**Description**: Get a single post by ID.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `post_id` (required, integer): Post ID

**Response** (200 OK):
```json
{
  "id": 1,
  "content": "Great tip for cotton farming!",
  "author_id": 1,
  "author": {
    "id": 1,
    "name": "John Doe",
    "email": "farmer@example.com"
  },
  "author_name": "John Doe",
  "region": "Maharashtra",
  "crop": "cotton",
  "category": "tip",
  "likes_count": 5,
  "comments_count": 2,
  "image_url": "/community/images/abc123.jpg",
  "created_at": "2024-01-15T10:30:00Z",
  "is_liked": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Post not found

---

### 4. PUT `/community/posts/{post_id}`

**Description**: Update a post. Only the author can update their own post.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `post_id` (required, integer): Post ID

**Request Body** (all fields optional):
```json
{
  "content": "Updated content",
  "crop": "wheat",
  "category": "question",
  "image_url": "/community/images/new123.jpg"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "content": "Updated content",
  "author_id": 1,
  "author": {
    "id": 1,
    "name": "John Doe",
    "email": "farmer@example.com"
  },
  "author_name": "John Doe",
  "region": "Maharashtra",
  "crop": "wheat",
  "category": "question",
  "likes_count": 5,
  "comments_count": 2,
  "image_url": "/community/images/new123.jpg",
  "created_at": "2024-01-15T10:30:00Z",
  "is_liked": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: You can only edit your own posts
- `404 Not Found`: Post not found
- `500 Internal Server Error`: Error updating post

---

### 5. DELETE `/community/posts/{post_id}`

**Description**: Delete a post. Only the author can delete their own post.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `post_id` (required, integer): Post ID

**Response** (204 No Content): Empty response body

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: You can only delete your own posts
- `404 Not Found`: Post not found
- `500 Internal Server Error`: Error deleting post

---

### 6. POST `/community/posts/{post_id}/like`

**Description**: Like or unlike a post (toggle).

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `post_id` (required, integer): Post ID

**Response** (200 OK):
```json
{
  "post_id": 1,
  "likes_count": 6,
  "is_liked": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Post not found

---

### 7. GET `/community/posts/{post_id}/comments`

**Description**: Get all comments for a post.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `post_id` (required, integer): Post ID

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "post_id": 1,
    "user_id": 2,
    "author_name": "Jane Smith",
    "content": "This is very helpful!",
    "created_at": "2024-01-15T11:00:00Z"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Post not found

---

### 8. POST `/community/posts/{post_id}/comments`

**Description**: Add a comment to a post.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `post_id` (required, integer): Post ID

**Request Body**:
```json
{
  "content": "This is very helpful!"
}
```

**Required Fields**: `content`

**Response** (201 Created):
```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "author_name": "Jane Smith",
  "content": "This is very helpful!",
  "created_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Post not found
- `422 Unprocessable Entity`: Validation error

---

### 9. GET `/community/user/{user_id}/posts`

**Description**: Get all posts created by a specific user.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id` (required, integer): User ID

**Query Parameters**:
- `skip` (optional, integer, default: 0): Number of posts to skip
- `limit` (optional, integer, default: 50): Maximum number of posts to return

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "content": "Great tip for cotton farming!",
    "author_id": 1,
    "author": {
      "id": 1,
      "name": "John Doe",
      "email": "farmer@example.com"
    },
    "author_name": "John Doe",
    "region": "Maharashtra",
    "crop": "cotton",
    "category": "tip",
    "likes_count": 5,
    "comments_count": 2,
    "image_url": null,
    "created_at": "2024-01-15T10:30:00Z",
    "is_liked": false
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found
- `500 Internal Server Error`: Error fetching user posts

---

### 10. GET `/community/top-contributors`

**Description**: Get top contributors by post count.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `limit` (optional, integer, default: 10): Number of contributors to return

**Response** (200 OK):
```json
[
  {
    "user_id": 1,
    "name": "John Doe",
    "posts_count": 15
  },
  {
    "user_id": 2,
    "name": "Jane Smith",
    "posts_count": 12
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

---

### 11. GET `/community/trending`

**Description**: Get trending hashtags from all posts.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `limit` (optional, integer, default: 10): Number of trending topics to return

**Response** (200 OK):
```json
[
  {
    "tag": "cotton",
    "count": 25
  },
  {
    "tag": "irrigation",
    "count": 18
  },
  {
    "tag": "pestcontrol",
    "count": 12
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Error fetching trending topics

---

### 12. GET `/community/posts/search`

**Description**: Search posts by content, author name, or crop.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `q` (required, string): Search query
- `skip` (optional, integer, default: 0): Number of posts to skip
- `limit` (optional, integer, default: 50): Maximum number of posts to return

**Example Request**:
```
GET /community/posts/search?q=cotton&skip=0&limit=20
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "content": "Great tip for cotton farming!",
    "author_id": 1,
    "author": {
      "id": 1,
      "name": "John Doe",
      "email": "farmer@example.com"
    },
    "author_name": "John Doe",
    "region": "Maharashtra",
    "crop": "cotton",
    "category": "tip",
    "likes_count": 5,
    "comments_count": 2,
    "image_url": null,
    "created_at": "2024-01-15T10:30:00Z",
    "is_liked": false
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

---

### 13. POST `/community/upload-image`

**Description**: Upload an image file for use in posts.

**Authentication**: Required (Bearer token)

**Request**: Multipart form data
- `file` (required, file): Image file (JPG, JPEG, PNG, GIF, WEBP)
- Maximum file size: 5MB

**Response** (200 OK):
```json
{
  "url": "/community/images/32cff42b-b34c-4899-8c92-5d97860d4aa0.png"
}
```

**Error Responses**:
- `400 Bad Request`: No filename provided, invalid file type, or file too large
- `401 Unauthorized`: Invalid or missing token

---

### 14. GET `/community/images/{filename}`

**Description**: Serve uploaded images.

**Authentication**: Not required (Public endpoint)

**Path Parameters**:
- `filename` (required, string): Image filename

**Response** (200 OK): Image file (binary)

**Error Responses**:
- `404 Not Found`: Image not found

---

## AI Chatbot Endpoints

**Base Path**: `/ai`

### 1. POST `/ai/chat`

**Description**: Chat with AI bot (AgriBot) powered by Google Gemini 2.5 Pro.

**Authentication**: Not required (Public endpoint)

**Request Body**:
```json
{
  "message": "What is the best time to plant rice?"
}
```

**Required Fields**: `message`

**Response** (200 OK):
```json
{
  "reply": "The best time to plant rice depends on your region. In most parts of India, rice is typically planted during the monsoon season (June-July) for kharif crops, or in January-February for rabi crops. Make sure the soil temperature is around 20-30°C and there's adequate water availability."
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error (missing message)
- `500 Internal Server Error`: Error generating AI response or no response from AI

---

## Root Endpoint

### GET `/`

**Description**: API root endpoint.

**Authentication**: Not required (Public endpoint)

**Response** (200 OK):
```json
{
  "message": "Welcome to KrushiRakshak Backend API"
}
```

---

## API Documentation Access

### Interactive API Documentation

The API provides automatic interactive documentation:

- **Swagger UI**: Available at `http://localhost:8000/docs`
  - Interactive API testing
  - Try out endpoints directly
  - View request/response schemas
  - Test authentication

- **ReDoc**: Available at `http://localhost:8000/redoc`
  - Alternative documentation format
  - Clean, readable interface
  - Complete API reference

- **OpenAPI Schema**: Available at `http://localhost:8000/openapi.json`
  - Machine-readable API specification
  - Can be imported into API testing tools
  - Used for code generation

---

## Implementation Screenshots

*Note: Screenshots would be added here during the final documentation phase. Placeholders are provided for key application screens.*

### Dashboard View
**Placeholder**: Screenshot of the main dashboard showing weather data, market prices, alerts, and crop health summary.

### Advisory Page
**Placeholder**: Screenshot of crop-specific advisory page displaying recommendations, risk analysis, and actionable insights.

### Community Feed
**Placeholder**: Screenshot of the community page showing posts, likes, comments, and filtering options.

### AI Chatbot Interface
**Placeholder**: Screenshot of the AgriBot chatbot interface with example conversation.

### User Profile
**Placeholder**: Screenshot of user profile page with editable fields and user statistics.

### Mobile View
**Placeholder**: Screenshot of the application running on a mobile device, demonstrating responsive design.

### Offline Mode
**Placeholder**: Screenshot showing offline banner and cached data access.

---

## Results & Impact

### System Performance

KrushiRakshak has been successfully implemented as a full-stack Progressive Web Application with the following achievements:

#### **Technical Achievements**

1. **Integrated Data Sources**
   - Successfully integrated real-time weather data from Open-Meteo API
   - Implemented market price fetching from Agmarknet with fallback mechanisms
   - Integrated satellite NDVI data processing (with synthetic data for development)
   - Created unified data pipeline combining multiple external sources

2. **Intelligent Advisory System**
   - Developed rule-based Fusion Engine with 50+ agricultural rules
   - Implemented multi-category rule evaluation (pest, irrigation, market)
   - Created dynamic advisory generation based on real-time conditions
   - Achieved rule scoring system with severity assessment

3. **User Experience**
   - Built responsive, mobile-first Progressive Web Application
   - Implemented offline functionality with service worker caching
   - Created intuitive UI with shadcn/ui components
   - Achieved multi-language support (English, Marathi)

4. **Community Features**
   - Implemented full CRUD operations for posts
   - Created like and comment system with real-time updates
   - Built image upload and serving functionality
   - Developed search, filtering, and trending topics features

5. **AI Integration**
   - Successfully integrated Google Gemini 2.5 Pro for agricultural advice
   - Implemented farmer-friendly system prompts
   - Created error handling for AI responses

### Functional Capabilities

#### **Data Integration**
- ✅ Real-time weather data fetching and processing
- ✅ Market price data with trend analysis
- ✅ NDVI-based crop health monitoring
- ✅ Location-based geocoding and reverse geocoding
- ✅ Crop stage detection and analysis

#### **Advisory Generation**
- ✅ Rule-based risk detection (pest, irrigation, market)
- ✅ Priority-based recommendation system
- ✅ Severity assessment and scoring
- ✅ Crop-specific advisory generation
- ✅ Context-aware recommendations

#### **User Features**
- ✅ User authentication and profile management
- ✅ Personalized dashboard with location-based data
- ✅ Crop-specific advisory access
- ✅ Community engagement (posts, likes, comments)
- ✅ AI chatbot for instant advice
- ✅ Offline data access

### Expected Impact

#### **For Farmers**

1. **Improved Decision Making**
   - Access to real-time weather forecasts helps farmers plan agricultural activities
   - Market price information enables better selling decisions
   - Crop health monitoring allows early detection of issues

2. **Risk Reduction**
   - Early warning system for pests and diseases
   - Weather alerts prevent crop damage
   - Data-driven recommendations reduce resource waste

3. **Knowledge Access**
   - Community platform facilitates peer learning
   - AI chatbot provides 24/7 agricultural advice
   - Regional knowledge sharing improves farming practices

4. **Accessibility**
   - Works offline in areas with poor connectivity
   - Multi-language support reaches diverse communities
   - Mobile-first design ensures easy access

#### **For Agriculture Sector**

1. **Technology Adoption**
   - Makes advanced agricultural technology accessible
   - Reduces barriers to entry for digital farming tools
   - Promotes data-driven agriculture

2. **Sustainability**
   - Optimized resource usage through informed decisions
   - Reduced pesticide and water waste
   - Improved crop yields through better management

3. **Community Building**
   - Connects farmers across regions
   - Facilitates knowledge exchange
   - Builds supportive agricultural network

### Metrics & KPIs

**Technical Metrics**:
- API Response Time: < 2 seconds for most endpoints
- Offline Cache Size: Optimized for mobile devices
- Database Query Performance: Indexed for fast retrieval
- Frontend Bundle Size: Optimized with code splitting

**User Experience Metrics**:
- Page Load Time: < 3 seconds on 3G connection
- Offline Functionality: Full feature access without internet
- Mobile Responsiveness: Works on all screen sizes
- Language Support: 2 languages (expandable)

**Feature Completeness**:
- Authentication System: ✅ Complete
- Dashboard: ✅ Complete
- Advisory System: ✅ Complete
- Community Platform: ✅ Complete
- AI Chatbot: ✅ Complete
- Offline Support: ✅ Complete
- Multi-language: ✅ Complete

---

## Limitations

While KrushiRakshak provides comprehensive functionality, there are several limitations that should be acknowledged:

### 1. **Data Source Dependencies**

- **External API Reliability**: The system depends on external APIs (Open-Meteo, Agmarknet) which may experience downtime or rate limiting
- **Satellite Data**: Currently uses synthetic NDVI data for development; real Bhuvan satellite integration requires additional setup and API access
- **Market Data Coverage**: Market prices may not be available for all crops or regions
- **Weather Data Accuracy**: Weather forecasts depend on third-party accuracy and may vary by location

### 2. **Rule-Based System Limitations**

- **Static Rules**: The Fusion Engine uses predefined rules that may not cover all agricultural scenarios
- **Regional Variations**: Rules may not account for all regional farming practices and conditions
- **Crop Coverage**: Advisory rules are primarily focused on major crops (cotton, wheat, rice); limited support for specialty crops
- **Rule Maintenance**: Adding new rules requires code updates and deployment

### 3. **Scalability Considerations**

- **Database**: Currently uses SQLite/PostgreSQL; may require optimization for large-scale deployment
- **Image Storage**: Image uploads stored locally; may need cloud storage (S3, Cloudinary) for production
- **API Rate Limits**: External API rate limits may affect concurrent user access
- **Caching Strategy**: Current caching may need enhancement for high-traffic scenarios

### 4. **Offline Functionality**

- **Data Freshness**: Offline data may become stale; no automatic background sync mechanism
- **Storage Limits**: Mobile device storage limits may restrict offline cache size
- **Initial Load**: First-time users need internet connection for initial data download

### 5. **User Experience**

- **Language Support**: Currently supports English and Marathi; additional languages require translation resources
- **Accessibility**: Limited accessibility features for users with disabilities
- **Browser Compatibility**: PWA features may vary across different browsers
- **Installation**: Users need to manually install PWA; no automatic installation prompt in all browsers

### 6. **AI Chatbot Limitations**

- **Context Awareness**: Chatbot does not maintain conversation context across sessions
- **Response Accuracy**: AI responses depend on training data and may not always be accurate
- **Regional Specificity**: May not provide region-specific advice without additional context
- **API Costs**: Google Gemini API usage incurs costs that scale with usage

### 7. **Security & Privacy**

- **Data Encryption**: Sensitive data transmission uses HTTPS; additional encryption may be needed for stored data
- **User Data**: User location and crop data stored in database; privacy policy and data protection measures needed
- **Authentication**: JWT tokens have expiration; refresh token mechanism not implemented
- **Image Security**: Uploaded images not scanned for malicious content

### 8. **Testing & Quality Assurance**

- **Test Coverage**: Limited automated test coverage; manual testing primarily used
- **Error Handling**: Basic error handling implemented; comprehensive error recovery needed
- **Performance Testing**: Limited load testing and performance optimization
- **Browser Testing**: Testing primarily on modern browsers; older browser support not verified

### 9. **Documentation & Support**

- **User Documentation**: Limited user guides and tutorials
- **Admin Documentation**: No admin panel or documentation for content management
- **API Documentation**: Auto-generated Swagger docs available; additional examples needed
- **Support System**: No built-in support ticket or help desk system

### 10. **Deployment & Infrastructure**

- **Production Deployment**: Current setup optimized for development; production deployment configuration needed
- **Monitoring**: No application monitoring or logging system implemented
- **Backup Strategy**: Database backup and recovery procedures not automated
- **CDN**: Static assets not served through CDN; may affect global performance

---

## Future Enhancements

Based on the current implementation and identified limitations, the following enhancements are recommended for future development:

### 1. **Advanced Data Integration**

- **Real Satellite Integration**: Integrate with Bhuvan API for actual NDVI data instead of synthetic data
- **IoT Sensor Integration**: Connect with soil moisture sensors, weather stations, and other IoT devices
- **Historical Data Analysis**: Implement historical data storage and trend analysis
- **Multiple Weather Sources**: Integrate with multiple weather APIs for redundancy and accuracy
- **Government Alert Integration**: Real-time integration with government agricultural alerts and advisories

### 2. **Machine Learning & AI Enhancements**

- **Predictive Analytics**: Implement ML models for crop yield prediction
- **Disease Detection**: Computer vision models for pest and disease identification from images
- **Price Forecasting**: ML-based market price prediction
- **Personalized Recommendations**: User behavior-based recommendation system
- **Chatbot Context**: Maintain conversation context and user history in AI chatbot

### 3. **Enhanced Advisory System**

- **Dynamic Rule Engine**: Web-based rule editor for adding/modifying rules without code deployment
- **Expert Validation**: System for agricultural experts to validate and improve rules
- **Multi-Crop Support**: Expand advisory coverage to more crops and specialty crops
- **Regional Customization**: Region-specific rule sets based on local farming practices
- **Seasonal Adjustments**: Automatic rule adjustments based on crop seasons

### 4. **Community Features**

- **Expert Verification**: Badge system for verified agricultural experts
- **Post Moderation**: Automated and manual content moderation
- **Rich Media**: Support for video uploads and sharing
- **Notifications**: Push notifications for likes, comments, and mentions
- **Direct Messaging**: Private messaging between users
- **Groups/Forums**: Crop-specific or region-specific discussion groups

### 5. **User Experience Improvements**

- **Progressive Enhancement**: Enhanced PWA features with background sync
- **Accessibility**: WCAG 2.1 compliance for users with disabilities
- **Dark Mode**: Theme switching with dark mode support
- **Customization**: User-customizable dashboard layouts
- **Tutorial System**: Interactive onboarding and feature tutorials
- **Feedback System**: In-app feedback and rating mechanism

### 6. **Mobile App Development**

- **Native Mobile Apps**: Develop native iOS and Android applications
- **Offline Sync**: Advanced offline synchronization with conflict resolution
- **Push Notifications**: Native push notification support
- **Camera Integration**: Direct camera access for crop health photos
- **GPS Integration**: Enhanced location services with field mapping

### 7. **Analytics & Reporting**

- **User Analytics**: Track user engagement and feature usage
- **Advisory Effectiveness**: Measure impact of advisories on user actions
- **Crop Performance**: Aggregate crop performance data across users
- **Regional Insights**: Regional agricultural trends and insights
- **Admin Dashboard**: Comprehensive admin dashboard for system monitoring

### 8. **Financial Features**

- **Crop Insurance Integration**: Integration with crop insurance providers
- **Loan Services**: Connect farmers with agricultural loan services
- **Marketplace**: Direct marketplace for buying/selling agricultural products
- **Payment Integration**: Payment gateway for premium features or services
- **Financial Planning**: Tools for agricultural financial planning

### 9. **Educational Content**

- **Video Library**: Educational videos on farming techniques
- **Interactive Guides**: Step-by-step guides for common farming tasks
- **Crop Calendar**: Interactive crop calendar with planting/harvesting dates
- **Best Practices**: Curated best practices library
- **Certification Programs**: Online agricultural certification courses

### 10. **Infrastructure & Scalability**

- **Microservices Architecture**: Break down monolith into microservices
- **Cloud Deployment**: Deploy to cloud infrastructure (AWS, GCP, Azure)
- **CDN Integration**: Content delivery network for global performance
- **Database Optimization**: Advanced indexing and query optimization
- **Caching Layer**: Redis-based caching for improved performance
- **Load Balancing**: Implement load balancing for high availability

### 11. **Security Enhancements**

- **Two-Factor Authentication**: 2FA for enhanced account security
- **Data Encryption**: End-to-end encryption for sensitive data
- **Rate Limiting**: Advanced rate limiting and DDoS protection
- **Security Audits**: Regular security audits and penetration testing
- **Compliance**: GDPR and data protection compliance measures

### 12. **Integration & APIs**

- **Third-Party Integrations**: Integration with other agricultural platforms
- **API Marketplace**: Public API for third-party developers
- **Webhook Support**: Webhook system for real-time integrations
- **Export Features**: Data export functionality (PDF, Excel, CSV)
- **Import Features**: Bulk data import for farmers with existing records

### 13. **Gamification & Engagement**

- **Achievement System**: Badges and achievements for user engagement
- **Leaderboards**: Community leaderboards for top contributors
- **Challenges**: Farming challenges and competitions
- **Rewards Program**: Reward system for active users
- **Referral System**: User referral program for growth

### 14. **Research & Development**

- **A/B Testing Framework**: Framework for testing new features
- **User Research**: Regular user research and feedback collection
- **Agronomic Research**: Collaboration with agricultural research institutions
- **Data Sharing**: Anonymized data sharing for agricultural research
- **Open Source Components**: Open source certain components for community contribution

---

## Conclusion

KrushiRakshak is our attempt to make advanced farming technology available to Indian farmers. We combined different data sources, built a smart advisory system, and created a community where farmers can help each other. This helps solve real problems that farmers face every day.

### What We Built

The project shows we can:

1. **Build Modern Apps**: Used React, FastAPI, and PostgreSQL to create a solid system
2. **Combine Data Sources**: Successfully connected weather, market, and satellite data
3. **Make Smart Systems**: Built a rule-based Fusion Engine and AI chatbot that give useful advice
4. **Design for Users**: Created a web app that works offline and supports multiple languages
5. **Build Community**: Made a platform where farmers can share knowledge and help each other

### What It Can Do

KrushiRakshak can help:

- **Grow More Crops**: By using data to make better decisions and catch problems early
- **Earn More Money**: By showing farmers the best time to sell and reducing losses
- **Learn More**: Through the community and AI chatbot
- **Use Resources Better**: By encouraging smart use of water, fertilizer, and pesticides
- **Bridge the Gap**: By making technology simple enough for all farmers to use

### Problems We Solved

The app directly fixes the problems we identified:

- ✅ **Real-Time Information**: Combined weather, market, and crop health data in one place
- ✅ **One Platform**: Everything farmers need in a single app
- ✅ **Easy to Use**: Simple design that doesn't require tech knowledge
- ✅ **Works Offline**: Functions even without internet
- ✅ **Community Help**: A place where farmers can share knowledge
- ✅ **Early Warnings**: Alerts farmers about problems before they get serious

### Looking Ahead

As we continue working on KrushiRakshak, we want it to become the main digital tool for Indian farmers, helping them from planting to harvest. We plan to add machine learning, connect with IoT devices, and expand community features to keep up with what farmers need.

By combining technology, data, and community, we're creating something that helps farmers make better decisions, avoid losses, and improve their lives. KrushiRakshak isn't just an app—it's our way of making farming smarter and more sustainable.

---

## References

### Technologies & Frameworks

1. **React** - JavaScript library for building user interfaces
   - Official Documentation: https://react.dev/

2. **FastAPI** - Modern Python web framework
   - Official Documentation: https://fastapi.tiangolo.com/

3. **TypeScript** - Typed superset of JavaScript
   - Official Documentation: https://www.typescriptlang.org/

4. **SQLAlchemy** - Python SQL toolkit and ORM
   - Official Documentation: https://www.sqlalchemy.org/

5. **Google Gemini** - AI model for chatbot
   - Official Documentation: https://ai.google.dev/

6. **Vite** - Next-generation frontend build tool
   - Official Documentation: https://vitejs.dev/

7. **Tailwind CSS** - Utility-first CSS framework
   - Official Documentation: https://tailwindcss.com/

8. **shadcn/ui** - Re-usable components built with Radix UI and Tailwind CSS
   - Official Documentation: https://ui.shadcn.com/

### Data Sources & APIs

1. **Open-Meteo** - Weather API
   - Website: https://open-meteo.com/

2. **Agmarknet** - Agricultural Marketing Information Network
   - Website: https://agmarknet.gov.in/

3. **Bhuvan** - Indian Geo-Platform of ISRO
   - Website: https://bhuvan.nrsc.gov.in/

4. **Nominatim** - OpenStreetMap geocoding service
   - Website: https://nominatim.org/

### Standards & Specifications

1. **Progressive Web Apps (PWA)**
   - MDN Web Docs: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps

2. **JWT (JSON Web Tokens)**
   - RFC 7519: https://tools.ietf.org/html/rfc7519

3. **RESTful API Design**
   - REST API Tutorial: https://restfulapi.net/

4. **OpenAPI Specification**
   - Official Specification: https://swagger.io/specification/

### Agricultural Resources

1. **India Meteorological Department (IMD)**
   - Website: https://mausam.imd.gov.in/

2. **Ministry of Agriculture & Farmers Welfare**
   - Website: https://agriculture.gov.in/

3. **Agricultural Research Data**
   - ICAR: https://www.icar.org.in/

### Development Tools

1. **Git** - Version control system
   - Official Website: https://git-scm.com/

2. **PostgreSQL** - Open-source relational database
   - Official Website: https://www.postgresql.org/

3. **Uvicorn** - ASGI server implementation
   - Official Documentation: https://www.uvicorn.org/

4. **Pydantic** - Data validation using Python type annotations
   - Official Documentation: https://docs.pydantic.dev/

### Additional Resources

1. **React Query** - Data fetching library for React
   - Official Documentation: https://tanstack.com/query

2. **i18next** - Internationalization framework
   - Official Documentation: https://www.i18next.com/

3. **Workbox** - JavaScript libraries for Progressive Web Apps
   - Official Documentation: https://developers.google.com/web/tools/workbox

4. **Axios** - HTTP client for JavaScript
   - Official Documentation: https://axios-http.com/

---

**Document Version**: 1.0.0  
**Last Updated**: [Date Placeholder]  
**Document Status**: Complete

---

*End of Documentation*

