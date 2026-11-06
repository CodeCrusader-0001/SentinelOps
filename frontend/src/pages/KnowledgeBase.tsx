import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { KnowledgeDocument, SearchResult } from '../types';
import { BookOpen, Search, Sparkles, FileText, ArrowRight } from 'lucide-react';

export const KnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<KnowledgeDocument | null>(null);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/knowledge/documents');
      const docs = resp.data || [];
      setDocuments(docs);
      if (docs.length > 0 && !selectedDoc) {
        setSelectedDoc(docs[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const resp = await api.post('/knowledge/search', {
        query: searchQuery,
        top_k: 4,
        threshold: 0.25
      });
      setSearchResults(resp.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">RAG Troubleshooting Knowledge Base</h1>
          <p className="text-xs text-gray-400 mt-1">Vectorized runbooks embedded with all-MiniLM-L6-v2 in FAISS</p>
        </div>
      </div>

      {/* Semantic Vector Search Box */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-5 shadow-xl space-y-3">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search runbooks via vector similarity (e.g. 'connection pool exhausted', 'OOM crash', 'CPU thrashing')..."
              className="w-full bg-[#111118] border border-[#242436] focus:border-cyan-500 rounded-lg py-2.5 pl-10 pr-4 text-xs text-gray-100 placeholder-gray-600 focus:outline-none transition"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="flex items-center space-x-2 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-xs rounded-lg transition shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>{searching ? 'Vector Searching...' : 'Vector Search'}</span>
          </button>
        </form>

        {/* Semantic Search Matches */}
        {searchResults.length > 0 && (
          <div className="pt-4 border-t border-[#242436] space-y-3">
            <div className="text-xs font-mono uppercase text-cyan-400 tracking-wider">
              Vector Match Results (Cosine Similarity Cutoff &ge; 0.25):
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {searchResults.map((res, i) => (
                <div key={i} className="p-3.5 rounded-lg bg-[#111118] border border-[#242436] space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-white">{res.document_title}</span>
                    <span className="text-cyan-400 font-mono text-[11px] bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                      Score: {(res.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 line-clamp-3 font-mono leading-relaxed">{res.chunk_content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Runbook Browser */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-[#151521] border border-[#242436] rounded-xl p-4 shadow-xl space-y-2">
          <div className="text-xs font-mono uppercase text-gray-400 px-2 pb-2 border-b border-[#242436]">
            Standard Operating Procedures ({documents.length})
          </div>
          <div className="space-y-1">
            {documents.map((doc) => (
              <button
                key={doc.id}
                onClick={() => setSelectedDoc(doc)}
                className={`w-full text-left p-3 rounded-lg text-xs transition flex items-center justify-between ${
                  selectedDoc?.id === doc.id
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-gray-300 hover:bg-[#111118] border border-transparent'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <FileText className="w-3.5 h-3.5 text-gray-500" />
                  <span className="font-medium">{doc.title}</span>
                </div>
                <span className="text-[10px] font-mono text-gray-500">{doc.chunk_count} chunks</span>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl">
          {selectedDoc ? (
            <div className="space-y-4">
              <div className="border-b border-[#242436] pb-3 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white">{selectedDoc.title}</h2>
                  <div className="text-xs text-gray-500 font-mono">Category: {selectedDoc.category} | Chunks in FAISS: {selectedDoc.chunk_count}</div>
                </div>
              </div>
              <pre className="text-xs text-gray-300 font-sans whitespace-pre-wrap leading-relaxed bg-[#111118] p-5 rounded-lg border border-[#242436] max-h-[600px] overflow-y-auto">
                {selectedDoc.content}
              </pre>
            </div>
          ) : (
            <div className="text-center py-20 text-gray-500 font-mono text-xs">
              Select a runbook from the left panel to inspect procedures.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

