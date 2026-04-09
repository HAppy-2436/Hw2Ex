from flask import Blueprint, request, jsonify
from models import db, KnowledgeNode, Book

bp = Blueprint('knowledge_nodes', __name__, url_prefix='/api/nodes')

def build_tree(node):
    """递归构建树状结构"""
    result = node.to_dict()
    children = KnowledgeNode.query.filter_by(parent_id=node.id).order_by(KnowledgeNode.order_index).all()
    result['children'] = [build_tree(child) for child in children]
    return result


@bp.route('', methods=['GET'])
def get_knowledge_nodes():
    """获取所有知识点（支持 ?book_id= 过滤）"""
    book_id = request.args.get('book_id')
    
    query = KnowledgeNode.query
    
    if book_id:
        query = query.filter_by(book_id=book_id)
    
    nodes = query.order_by(KnowledgeNode.order_index).all()
    return jsonify([node.to_dict() for node in nodes])


@bp.route('/tree', methods=['GET'])
def get_knowledge_tree():
    """获取完整知识树（按 book_id 组织，嵌套父子关系）"""
    book_id = request.args.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'book_id is required'}), 400
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 获取顶级节点（parent_id 为 None）
    root_nodes = KnowledgeNode.query.filter_by(
        book_id=book_id, 
        parent_id=None
    ).order_by(KnowledgeNode.order_index).all()
    
    tree = [build_tree(node) for node in root_nodes]
    
    return jsonify({
        'book_id': book_id,
        'book_title': book.title,
        'tree': tree
    })


@bp.route('', methods=['POST'])
def create_knowledge_node():
    """创建新知识点"""
    data = request.get_json()
    
    required_fields = ['book_id', 'title']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if 'parent_id' in data and data['parent_id']:
        parent = KnowledgeNode.query.get(data['parent_id'])
        if not parent:
            return jsonify({'error': 'Parent node not found'}), 404
        if parent.book_id != book.id:
            return jsonify({'error': 'Parent node must belong to the same book'}), 400
    
    node = KnowledgeNode(
        book_id=data['book_id'],
        parent_id=data.get('parent_id'),
        title=data['title'],
        level=data.get('level', 0),
        order_index=data.get('order_index', 0),
        page_start=data.get('page_start'),
        page_end=data.get('page_end'),
        content=data.get('content'),
        tags=data.get('tags')
    )
    
    db.session.add(node)
    db.session.commit()
    
    return jsonify(node.to_dict()), 201


@bp.route('/<int:node_id>', methods=['GET'])
def get_knowledge_node(node_id):
    """获取知识点详情"""
    node = KnowledgeNode.query.get_or_404(node_id)
    
    result = node.to_dict()
    
    children = KnowledgeNode.query.filter_by(parent_id=node_id).order_by(KnowledgeNode.order_index).all()
    result['children'] = [child.to_dict() for child in children]
    
    return jsonify(result)


@bp.route('/<int:node_id>', methods=['PUT'])
def update_knowledge_node(node_id):
    """更新知识点信息"""
    node = KnowledgeNode.query.get_or_404(node_id)
    data = request.get_json()
    
    if 'title' in data:
        node.title = data['title']
    if 'level' in data:
        node.level = data['level']
    if 'order_index' in data:
        node.order_index = data['order_index']
    if 'page_start' in data:
        node.page_start = data['page_start']
    if 'page_end' in data:
        node.page_end = data['page_end']
    if 'content' in data:
        node.content = data['content']
    if 'tags' in data:
        node.tags = data['tags']
    
    if 'parent_id' in data:
        new_parent_id = data['parent_id']
        if new_parent_id == node.id:
            return jsonify({'error': 'Node cannot be its own parent'}), 400
        
        if new_parent_id:
            parent = KnowledgeNode.query.get(new_parent_id)
            if not parent:
                return jsonify({'error': 'Parent node not found'}), 404
            if parent.book_id != node.book_id:
                return jsonify({'error': 'Parent node must belong to the same book'}), 400
            
            # 检查循环引用
            current = parent
            while current:
                if current.id == node.id:
                    return jsonify({'error': 'Circular reference detected'}), 400
                current = current.parent
        
        node.parent_id = new_parent_id
    
    db.session.commit()
    return jsonify(node.to_dict())


@bp.route('/<int:node_id>', methods=['DELETE'])
def delete_knowledge_node(node_id):
    """删除知识点（级联删除子节点）"""
    node = KnowledgeNode.query.get_or_404(node_id)
    
    def delete_node_and_children(n):
        """递归删除节点及其所有子节点"""
        children = KnowledgeNode.query.filter_by(parent_id=n.id).all()
        for child in children:
            delete_node_and_children(child)
        db.session.delete(n)
    
    delete_node_and_children(node)
    db.session.commit()
    
    return jsonify({'message': 'Knowledge node and all children deleted successfully'})


@bp.route('/<int:node_id>/children', methods=['GET'])
def get_node_children(node_id):
    """获取指定节点的直接子节点"""
    node = KnowledgeNode.query.get_or_404(node_id)
    children = KnowledgeNode.query.filter_by(parent_id=node_id).order_by(KnowledgeNode.order_index).all()
    return jsonify([child.to_dict() for child in children])


@bp.route('/<int:node_id>/ancestors', methods=['GET'])
def get_node_ancestors(node_id):
    """获取指定节点的祖先路径"""
    node = KnowledgeNode.query.get_or_404(node_id)
    
    ancestors = []
    current = node.parent
    while current:
        ancestors.append(current.to_dict())
        current = current.parent
    
    # 反转顺序，从根节点到父节点
    ancestors.reverse()
    
    return jsonify({
        'node_id': node_id,
        'ancestors': ancestors
    })


@bp.route('/<int:node_id>/tree', methods=['GET'])
def get_node_tree(node_id):
    """获取指定节点的完整子树"""
    node = KnowledgeNode.query.get_or_404(node_id)
    return jsonify(build_tree(node))