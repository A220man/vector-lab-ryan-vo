import React from 'react';
import type { IndexNode } from '../types';

interface IndexTreeProps {
  nodes: IndexNode[];
  level?: number;
  selectedNodeId?: string;
  onSelectNode?: (node: IndexNode) => void;
}

export const IndexTree: React.FC<IndexTreeProps> = ({
  nodes,
  level = 0,
  selectedNodeId,
  onSelectNode,
}) => {
  if (!nodes || nodes.length === 0) {
    return <div className="empty-tree">No index nodes</div>;
  }

  return (
    <ul className="index-tree" style={{ paddingLeft: level > 0 ? `${level * 20}px` : 0 }}>
      {nodes.map((node) => (
        <li key={node.node_id} className="tree-node">
          <div
            className={`node-header ${selectedNodeId === node.node_id ? 'selected' : ''}`}
            onClick={() => onSelectNode?.(node)}
            style={{ fontWeight: node.level === 0 ? 'bold' : 'normal' }}
          >
            <span className="node-structure">{node.structure || '•'}</span>
            <span className="node-title">{node.title}</span>
            {node.nodes && node.nodes.length > 0 && (
              <span className="node-children-count">({node.nodes.length})</span>
            )}
          </div>
          {node.nodes && node.nodes.length > 0 && (
            <IndexTree
              nodes={node.nodes}
              level={level + 1}
              selectedNodeId={selectedNodeId}
              onSelectNode={onSelectNode}
            />
          )}
        </li>
      ))}
    </ul>
  );
};