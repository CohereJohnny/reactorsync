"""
Knowledge Base SQLAlchemy model with pgvector support
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
from .base import Base

class KnowledgeBase(Base):
    """
    Knowledge base model for storing document embeddings
    
    Stores documents, manuals, procedures, and other knowledge
    with vector embeddings for semantic search capabilities.
    """
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI/Cohere embedding dimension
    doc_metadata = Column(JSONB)  # Additional document metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, document='{self.document_name}')>"

    def to_dict(self):
        """Convert knowledge base entry to dictionary for API responses"""
        return {
            "id": self.id,
            "document_name": self.document_name,
            "content": self.content,
            "metadata": self.doc_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "has_embedding": self.embedding is not None
        }

    @classmethod
    def create_from_dict(cls, data: dict):
        """Create knowledge base entry from dictionary data"""
        return cls(
            document_name=data["document_name"],
            content=data["content"],
            embedding=data.get("embedding"),
            doc_metadata=data.get("metadata", {})
        )

    def set_embedding(self, embedding_vector):
        """Set the embedding vector for this document"""
        self.embedding = embedding_vector

    @classmethod
    def search_similar(cls, db_session, query_embedding, limit=5, threshold=0.7):
        """
        Search for similar documents using vector similarity
        
        Args:
            db_session: SQLAlchemy session
            query_embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
        
        Returns:
            List of similar documents with similarity scores
        """
        from sqlalchemy import text
        
        # Use pgvector cosine similarity
        similarity_query = text("""
            SELECT *, (embedding <=> :query_embedding) as distance
            FROM knowledge_base 
            WHERE embedding IS NOT NULL
            AND (embedding <=> :query_embedding) < :threshold
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)
        
        results = db_session.execute(
            similarity_query,
            {
                "query_embedding": query_embedding,
                "threshold": 1.0 - threshold,  # Convert similarity to distance
                "limit": limit
            }
        ).fetchall()
        
        return [
            {
                "document": cls.from_row(row),
                "similarity": 1.0 - row.distance,  # Convert distance back to similarity
                "distance": row.distance
            }
            for row in results
        ]

    @classmethod
    def from_row(cls, row):
        """Create instance from database row"""
        instance = cls()
        for column in cls.__table__.columns:
            setattr(instance, column.name, getattr(row, column.name))
        return instance

    def get_document_type(self):
        """Get document type from metadata"""
        if self.doc_metadata:
            return self.doc_metadata.get("document_type", "unknown")
        return "unknown"

    def get_tags(self):
        """Get document tags from metadata"""
        if self.doc_metadata:
            return self.doc_metadata.get("tags", [])
        return []

    def add_tag(self, tag):
        """Add a tag to document metadata"""
        if not self.doc_metadata:
            self.doc_metadata = {}
        
        tags = self.doc_metadata.get("tags", [])
        if tag not in tags:
            tags.append(tag)
            self.doc_metadata["tags"] = tags

    def set_document_type(self, doc_type):
        """Set document type in metadata"""
        if not self.doc_metadata:
            self.doc_metadata = {}
        self.doc_metadata["document_type"] = doc_type
