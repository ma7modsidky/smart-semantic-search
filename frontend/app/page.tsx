'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion'; // Animation library
import SkeletonCard from '@/components/SkeletonCard';

interface Product {
  id: number;
  name: string;
  description: string;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    setLoading(true);
    setResults([]); // Clear old results to show skeletons
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/search?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 font-sans">
      <div className="max-w-3xl mx-auto">
        <header className="text-center mb-12">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-4"
          >
            Smart Search
          </motion.h1>
          <p className="text-gray-500 text-lg">AI-powered semantic discovery for your store.</p>
        </header>
        
        <form onSubmit={handleSearch} className="relative mb-12 group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What are you looking for today?"
            className="w-full p-5 pl-6 pr-32 rounded-2xl border-2 border-transparent bg-white shadow-xl focus:border-blue-500 focus:ring-0 outline-none text-black transition-all"
          />
          <button 
            type="submit"
            disabled={loading}
            className="absolute right-2 top-2 bottom-2 bg-blue-600 text-white px-6 rounded-xl font-bold hover:bg-blue-700 transition-all disabled:bg-blue-300"
          >
            {loading ? '...' : 'Search'}
          </button>
        </form>

        <div className="grid gap-6">
          <AnimatePresence mode="wait">
            {loading ? (
              // Show 3 skeleton cards while loading
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
              </motion.div>
            ) : (
              <motion.div key="results" className="space-y-4">
                {results.map((product, index) => (
                  <motion.div
                    key={product.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }} // Staggered entrance
                    className="p-6 bg-white rounded-xl shadow-sm border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all cursor-pointer"
                  >
                    <h2 className="text-xl font-bold text-gray-800">{product.name}</h2>
                    <p className="text-gray-600 mt-2 line-clamp-2">{product.description}</p>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </main>
  );
}