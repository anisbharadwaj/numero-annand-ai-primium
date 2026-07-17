from flask import Blueprint, request, jsonify, session
from app.models import db, User, AIChat
from datetime import datetime
import uuid

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# AI knowledge base for Annand AI assistant
AI_KNOWLEDGE_BASE = {
    'en': {
        'greeting': "Namaste! I'm Annand AI, your personal numerology guide. How can I help you today?",
        'pricing': "We offer:\n• Digital PDF Report: ₹201\n• Premium Printed Report: ₹501\n• Premium Subscription: ₹500/month (unlimited AI messages)",
        'ai_features': "As Annand AI, I can help you with:\n• Website navigation\n• Pricing information\n• Numerology basics\n• Report details\n• Payment process\n• Account management",
        'contact': "Contact us:\n📞 +91 7099805039\n💬 WhatsApp: https://wa.me/917099805039\n📧 Email: annand@numero.ai",
        'numerology': "Numerology is the study of numbers and their mystical significance. We focus on:\n• Lo Shu Grid\n• Chaldean & Vedic systems\n• Birth numbers, Destiny numbers\n• Life path analysis\n• Lucky numbers & dates",
        'payment': "Payment is secure via UPI:\n1. Scan the generated QR code\n2. Send payment to 7099805039-2@axl\n3. Submit your Transaction Reference (UTR)\n4. Verify payment in admin dashboard\n5. Download your report",
        'premium': "Premium Subscription at ₹500/month includes:\n• Unlimited AI assistant messages\n• Priority consultation booking\n• Exclusive numerology tips\n• Fast report processing",
    },
    'hi': {
        'greeting': "नमस्ते! मैं अन्नद एआई हूँ, आपका व्यक्तिगत अंकज्योतिष गाइड। मैं आपकी कैसे मदद कर सकता हूँ?",
        'pricing': "हमारी पेशकश:\n• डिजिटल PDF रिपोर्ट: ₹201\n• प्रीमियम मुद्रित रिपोर्ट: ₹501\n• प्रीमियम सदस्यता: ₹500/माह (असीमित एआई संदेश)",
        'contact': "संपर्क करें:\n📞 +91 7099805039\n💬 व्हाट्सएप: https://wa.me/917099805039",
        'payment': "यूपीआई के माध्यम से सुरक्षित भुगतान:\n1. जेनरेट किए गए क्यूआर कोड को स्कैन करें\n2. 7099805039-2@axl को भुगतान भेजें\n3. अपना लेनदेन संदर्भ (यूटीआर) जमा करें",
    },
    'as': {
        'greeting': "নমস্কাৰ! মই অন্নদ এআই, আপোনাৰ ব্যক্তিগত সংখ্যা বিজ্ঞান গাইড। আজ মই আপোনাক কিভাবে সহায়তা কৰিব পাৰো?",
        'pricing': "আমাদের অফার:\n• ডিজিটাল PDF প্রতিবেদন: ₹201\n• প্রিমিয়াম মুদ্রিত প্রতিবেদন: ₹501\n• প্রিমিয়াম সাবস্ক্রিপশন: ₹500/মাস (আনলিমিটেড এআই বার্তা)",
        'contact': "যোগাযোগ করুন:\n📞 +91 7099805039\n💬 হোয়াটসঅ্যাপ: https://wa.me/917099805039",
    }
}

def get_ai_response(user_message, language='en'):
    """Generate AI response based on keywords in user message."""
    message_lower = user_message.lower()
    kb = AI_KNOWLEDGE_BASE.get(language, AI_KNOWLEDGE_BASE['en'])
    
    # Match keywords and return relevant responses
    if any(word in message_lower for word in ['price', 'cost', 'payment', '₹', 'rupee']):
        return kb.get('pricing', kb['greeting'])
    elif any(word in message_lower for word in ['help', 'feature', 'what', 'can you']):
        return kb.get('ai_features', kb['greeting'])
    elif any(word in message_lower for word in ['contact', 'phone', 'whatsapp', 'email']):
        return kb.get('contact', kb['greeting'])
    elif any(word in message_lower for word in ['numerology', 'number', 'birth', 'destiny']):
        return kb.get('numerology', kb['greeting'])
    elif any(word in message_lower for word in ['pay', 'upi', 'qr', 'utr', 'transaction']):
        return kb.get('payment', kb['greeting'])
    elif any(word in message_lower for word in ['premium', 'subscription', 'unlimited']):
        return kb.get('premium', kb['greeting'])
    else:
        return kb.get('greeting', "I'm here to help! Feel free to ask about pricing, numerology, or how to use our services.")

def get_or_create_guest_session():
    """Get or create a guest session ID."""
    if 'guest_session_id' not in session:
        session['guest_session_id'] = str(uuid.uuid4())
    return session['guest_session_id']

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Handle AI chat messages with message limit enforcement."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        language = data.get('language', 'en')
        user_id = data.get('user_id')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Handle user authentication and message limits
        user = None
        remaining_messages = float('inf')
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                remaining_messages = user.get_ai_message_limit()
                if remaining_messages <= 0 and user.subscription_tier != 'premium':
                    return jsonify({
                        'error': f'Daily limit reached. Upgrade to Premium for unlimited access.',
                        'remaining': 0
                    }), 429
                user.increment_ai_messages()
        else:
            # Guest user - track by session
            guest_session_id = get_or_create_guest_session()
            # Simple guest limit tracking (5 per day)
            remaining_messages = 5
        
        # Generate AI response
        ai_response = get_ai_response(user_message, language)
        
        # Store chat in database
        chat_record = AIChat(
            user_id=user_id,
            session_id=get_or_create_guest_session() if not user_id else None,
            user_message=user_message,
            ai_response=ai_response,
            language=language
        )
        db.session.add(chat_record)
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'remaining_messages': remaining_messages if remaining_messages != float('inf') else 'unlimited',
            'chat_id': chat_record.id,
            'timestamp': chat_record.created_at.isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/message-limit', methods=['GET'])
def get_message_limit():
    """Get remaining AI messages for current user."""
    user_id = request.args.get('user_id')
    
    if user_id:
        user = User.query.get(user_id)
        if user:
            remaining = user.get_ai_message_limit()
            return jsonify({
                'remaining': remaining if remaining != float('inf') else 'unlimited',
                'tier': user.subscription_tier,
                'reset_at': (user.ai_message_reset_at + timedelta(hours=24)).isoformat()
            })
    
    return jsonify({'remaining': 5, 'tier': 'guest'})

@ai_bp.route('/chat-history/<int:user_id>', methods=['GET'])
def chat_history(user_id):
    """Get chat history for a user."""
    chats = AIChat.query.filter_by(user_id=user_id).order_by(AIChat.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': chat.id,
        'user_message': chat.user_message,
        'ai_response': chat.ai_response,
        'created_at': chat.created_at.isoformat()
    } for chat in chats])
