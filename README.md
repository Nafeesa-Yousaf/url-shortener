# URL Shortener API

> 🌐 **Live Demo:** [https://url-shortener-one-self.vercel.app/docs](https://url-shortener-one-self.vercel.app/docs)

A clean, production-ready URL shortener designed to demonstrate key patterns in **distributed systems** and **scalable backend architecture**. 

By coupling **FastAPI** with **PostgreSQL** and **Upstash Redis** (distributed in-memory cache), the system maintains high performance under heavy read traffic while keeping database lookup overhead to a minimum.

---

## 🎯 Architectural Challenges Addressed

1. **Database Bottlenecks & Scale-Out Reads:** 
   Relational databases can easily become a bottleneck when handling high-frequency read operations (e.g., millions of users clicking redirect links simultaneously). We address this by implementing a **Cache-Aside pattern** with Upstash Redis, offloading over 95% of redirect reads from PostgreSQL to memory.
2. **Collision-Free Key Generation:** 
   Instead of generating random strings and querying the database to check for duplicates (which causes database roundtrips and high contention), we utilize a deterministic sequence-to-string mapping via Base62 encoding.

---

## 🛠️ Tech Stack & Internal Approaches

* **Web Framework & Validation (FastAPI & Pydantic):**
  * **FastAPI** serves as the asynchronous web framework.
  * **Pydantic's** `HttpUrl` is used to enforce strict URL format validation on incoming data payloads.
* **Persistent Storage & Connection Management (PostgreSQL & psycopg2):**
  * PostgreSQL is our persistent database of record.
  * We use `psycopg2`'s `SimpleConnectionPool` alongside a custom Python context manager (`get_db`) to safely acquire, release, and rollback database transactions, preventing resource leaks.
* **Distributed Caching (Upstash Redis):**
  * We use **Upstash Redis** for cache-aside reads. We connect to it using the async-capable `upstash-redis` client, configuring a 15-day TTL for key eviction.
* **Identifier Generation (Base62 Encoding):**
  * A custom math-based **Base62 mapping** (`0-9`, `a-z`, `A-Z`) translates auto-incremented database IDs into compact short codes (and vice-versa). This guarantees collision-free lookup keys.
* **Hosting & Environment Config (Vercel & python-dotenv):**
  * The stateless API code is packaged for **Vercel** using `@vercel/python` serverless deployment.

---

## 🔄 How the Flow Works

Here is a visual representation of the application's data flow and request paths:

### Application Flow Diagram

![Application Flow Diagram](flow_diagram.png)


### Shortening a URL (`POST /url_shortner`)

1. **Request:** The user sends a long URL.
2. **Persistence:** The URL is inserted into PostgreSQL, which returns a guaranteed unique, auto-incrementing integer `ID`.
3. **Encoding:** We encode the unique database `ID` into a **Base62 string** (e.g., database ID `125` translates to a short code like `23`).
4. **Caching:** The key-value pair (`short_code -> original_url`) is written to Upstash Redis with a **15-day TTL (Time-To-Live)**.
5. **Response:** The API constructs and returns the shortened link.

### Resolving and Redirecting (`GET /{short_url}`)

1. **Request:** The client clicks the short URL.
2. **Cache Lookup:** FastAPI queries Redis (in-memory lookup).
3. **Cache Hit:** If found, the client is immediately redirected to the original URL with sub-millisecond latency and zero database load.
4. **Cache Miss & Self-Healing:** If the token is missing or expired from Redis:
   * The short code is decoded back into its integer ID.
   * The original URL is fetched from **PostgreSQL**.
   * **Cache Repair:** The URL is written *back* into Upstash Redis with a fresh 15-day TTL, ensuring all subsequent clicks result in an instant cache hit.
5. **Response:** The client is seamlessly redirected to their final destination.

---

## 🧠 Key Takeaways & What I Learned

Through this implementation, we explore and demonstrate several core system design concepts:

* **The Cache-Aside Pattern:** Designing robust fallback logic to handle cache misses while minimizing write amplification and keeping cache values consistent with persistent storage.
* **Deterministic Identifier Mapping:** Using Base62 encoding to generate clean short URLs from database IDs. This avoids hash collisions (unlike MD5/SHA256 truncation) and eliminates database lookups during key generation.
* **Distributed Cache Expiry (TTL):** Applying caching strategies (such as a 15-day TTL) to manage memory efficiently, ensuring hot links stay in memory while inactive links are naturally evicted.

---

## 🚀 How to Run Locally

### 1. Clone the repository and setup a virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate # On macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup your environment variables
Create a `.env` file in the root folder:
```env
DB_URL="postgresql://username:password@host:port/database"
UPSTASH_URL="https://your-upstash-redis-url.upstash.io"
UPSTASH_TOKEN="your_upstash_redis_token"
```

### 4. Run the development server
```bash
uvicorn main:app --reload
```
Open your browser at `http://127.0.0.1:8000/docs` to test the API endpoints using the interactive Swagger UI.

---

## 🌐 Deployment & Hosting

* **Live APP:** [https://url-shortener-one-self.vercel.app/docs](https://url-shortener-one-self.vercel.app/docs)
* **API Application:** Hosted on [Vercel](https://vercel.com) using Serverless Functions (configured inside `vercel.json`).
* **Cache:** Hosted on [Upstash](https://upstash.com) (Serverless Redis).
* **Database:** Hosted on Supabase (PostgreSQL provider).

---

## 🧹 Database Cleanup (Supabase Cron)

Since the Redis cache automatically expires keys after 15 days (`ex=1296000`), we have added a cron job in Supabase to keep the PostgreSQL database clean and lean by automatically purging old records.

This cron job runs every 15 days at midnight and deletes any database records from the `short_urls` table where the creation timestamp (`created_at`) is older than 15 days:

```sql
select cron.schedule(
  'prune-expired-urls',
  '0 0 */15 * *', -- Runs every 15 days at midnight
  $$ delete from short_urls where created_at < now() - interval '15 days' $$
);
```

