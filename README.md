# 🎧 Graph-Based Music Recommendation System

A **Graph-based Music Recommendation System** that combines data from **Last.fm** and **Spotify**, and applies a **Random Walk on Hypergraph** approach to generate intelligent music recommendations.

The system is built with **Next.js** for the frontend and includes **interactive visualization using D3.js** to explore relationships between users, artists, and tracks.

---
# Full-view of platform
[[skill-exchangeplatform.vercel.app](https://skill-exchangeplatform.vercel.app/)](https://music-recommendation-frontend-murex.vercel.app/)
## 🚀 Features

* 🔗 Combines **Last.fm + Spotify datasets**
* 🧠 Uses **Hypergraph-based modeling**
* 🔄 Implements **Random Walk algorithm** for recommendations
* 📊 Interactive **graph visualization (D3.js)**
* ⚡ Built with **Next.js (React Framework)**
* 🌐 API routes for backend logic

---

## 🏗️ Tech Stack

* **Frontend:** Next.js, React, TypeScript
* **Visualization:** D3.js
* **Backend:** Next.js API Routes
* **Data Processing:** Python (for graph + preprocessing)
* **Datasets:** Last.fm, Spotify

---

## 📂 Project Structure

```
├── data/                  # Dataset files
├── data-collection/       # Scripts for collecting data
├── Graph/                 # Graph construction logic
├── public/                # Static assets
├── src/                  # Main frontend source code
├── pages/api/             # API routes
├── README.md
```

---

```
npm install
# or
yarn install
# or
pnpm install
```

---

###  the development server
```
npm run dev
```

Open 👉 http://localhost:3000

---

## 🧠 How It Works

1. 🎵 Merge datasets from **Spotify & Last.fm**
2. 🔗 Construct a **Hypergraph**

   * Nodes: Users, Artists, Tracks
   * Hyperedges: Relationships between them
3. 🚶 Apply **Random Walk algorithm**

   * Traverse graph to find relevant recommendations
4. 📊 Visualize using **D3.js**

   * Interactive exploration of recommendations

---

## 📡 API Endpoints

Example:

```
/api/hello
```

You can modify APIs inside:

```
pages/api/
```

---

## 🖥️ Visualization

* Interactive graph representation of music relationships
* Shows connections between:

  * Users 👤
  * Artists 🎤
  * Songs 🎶

---

## 📘 Learn More

* [Next.js Documentation](https://nextjs.org/docs)
* [D3.js Documentation](https://d3js.org/)
* Hypergraph & Random Walk → Refer to project report

---

## 🚀 Deployment

The easiest way to deploy:

👉 Use **Vercel**

```
npm run build
npm start
```
