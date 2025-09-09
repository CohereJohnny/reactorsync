"""
Knowledge Base Repository - Data access layer for knowledge base operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, text
from models.knowledge_base import KnowledgeBase
import structlog

logger = structlog.get_logger()

class KnowledgeBaseRepository:
    """Repository for knowledge base data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        document_type: Optional[str] = None
    ) -> List[KnowledgeBase]:
        """
        Get all knowledge base documents
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            document_type: Filter by document type
        """
        query = self.db.query(KnowledgeBase)
        
        if document_type:
            query = query.filter(
                KnowledgeBase.doc_metadata['document_type'].astext == document_type
            )
        
        return query.order_by(desc(KnowledgeBase.created_at)).offset(skip).limit(limit).all()

    def get_by_id(self, doc_id: int) -> Optional[KnowledgeBase]:
        """Get knowledge base document by ID"""
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.id == doc_id).first()

    def get_by_name(self, document_name: str) -> Optional[KnowledgeBase]:
        """Get knowledge base document by name"""
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.document_name == document_name
        ).first()

    def create(self, doc_data: Dict[str, Any]) -> KnowledgeBase:
        """
        Create a new knowledge base document
        
        Args:
            doc_data: Dictionary containing document information
        """
        doc = KnowledgeBase.create_from_dict(doc_data)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        
        logger.info("Knowledge base document created", 
                   doc_id=doc.id,
                   document_name=doc.document_name)
        return doc

    def update_embedding(self, doc_id: int, embedding_vector: List[float]) -> Optional[KnowledgeBase]:
        """
        Update document embedding
        
        Args:
            doc_id: Document ID
            embedding_vector: Vector embedding
        """
        doc = self.get_by_id(doc_id)
        if not doc:
            return None
        
        doc.set_embedding(embedding_vector)
        self.db.commit()
        self.db.refresh(doc)
        
        logger.info("Document embedding updated", doc_id=doc_id)
        return doc

    def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 5,
        threshold: float = 0.7,
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
            document_type: Optional filter by document type
        """
        # Build the similarity query
        similarity_query = """
            SELECT *, (embedding <=> :query_embedding) as distance
            FROM knowledge_base 
            WHERE embedding IS NOT NULL
            AND (embedding <=> :query_embedding) < :threshold
        """
        
        params = {
            "query_embedding": query_embedding,
            "threshold": 1.0 - threshold,  # Convert similarity to distance
            "limit": limit
        }
        
        # Add document type filter if specified
        if document_type:
            similarity_query += " AND doc_metadata->>'document_type' = :document_type"
            params["document_type"] = document_type
        
        similarity_query += " ORDER BY embedding <=> :query_embedding LIMIT :limit"
        
        results = self.db.execute(text(similarity_query), params).fetchall()
        
        return [
            {
                "document": {
                    "id": row.id,
                    "document_name": row.document_name,
                    "content": row.content,
                    "metadata": row.doc_metadata,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                },
                "similarity": 1.0 - row.distance,  # Convert distance back to similarity
                "distance": row.distance
            }
            for row in results
        ]

    def search_by_text(self, search_term: str) -> List[KnowledgeBase]:
        """
        Search documents by text content
        
        Args:
            search_term: Text to search for
        """
        return self.db.query(KnowledgeBase).filter(
            or_(
                KnowledgeBase.document_name.ilike(f"%{search_term}%"),
                KnowledgeBase.content.ilike(f"%{search_term}%")
            )
        ).order_by(desc(KnowledgeBase.created_at)).all()

    def get_by_tags(self, tags: List[str]) -> List[KnowledgeBase]:
        """
        Get documents by tags
        
        Args:
            tags: List of tags to search for
        """
        # Use JSONB containment operator to find documents with any of the tags
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(
                KnowledgeBase.doc_metadata['tags'].astext.contains(tag)
            )
        
        return self.db.query(KnowledgeBase).filter(
            or_(*tag_conditions)
        ).all()

    def get_by_document_type(self, document_type: str) -> List[KnowledgeBase]:
        """
        Get documents by type
        
        Args:
            document_type: Type of document to retrieve
        """
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.doc_metadata['document_type'].astext == document_type
        ).order_by(desc(KnowledgeBase.created_at)).all()

    def update(self, doc_id: int, update_data: Dict[str, Any]) -> Optional[KnowledgeBase]:
        """
        Update knowledge base document
        
        Args:
            doc_id: Document ID
            update_data: Fields to update
        """
        doc = self.get_by_id(doc_id)
        if not doc:
            return None
        
        # Update allowed fields
        allowed_fields = ['document_name', 'content', 'doc_metadata']
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(doc, field):
                setattr(doc, field, value)
        
        self.db.commit()
        self.db.refresh(doc)
        
        logger.info("Knowledge base document updated", 
                   doc_id=doc_id,
                   fields=list(update_data.keys()))
        return doc

    def delete(self, doc_id: int) -> bool:
        """
        Delete a knowledge base document
        
        Args:
            doc_id: Document ID to delete
        """
        doc = self.get_by_id(doc_id)
        if not doc:
            return False
        
        self.db.delete(doc)
        self.db.commit()
        
        logger.info("Knowledge base document deleted", doc_id=doc_id)
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        total_docs = self.db.query(KnowledgeBase).count()
        docs_with_embeddings = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.embedding.isnot(None)
        ).count()
        
        # Get document type distribution
        type_stats = self.db.query(
            KnowledgeBase.doc_metadata['document_type'].astext.label('doc_type'),
            func.count(KnowledgeBase.id).label('count')
        ).group_by('doc_type').all()
        
        type_distribution = {
            result.doc_type or 'unknown': result.count 
            for result in type_stats
        }
        
        return {
            "total_documents": total_docs,
            "documents_with_embeddings": docs_with_embeddings,
            "embedding_coverage": round((docs_with_embeddings / total_docs * 100) if total_docs > 0 else 0, 1),
            "document_types": type_distribution
        }
