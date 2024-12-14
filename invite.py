from anthropic import Anthropic
import os

# Initialize Anthropic client using environment variable
anthropic = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

def create_invite_text(party_details):
    """
    Generate party invite text using Claude API based on detailed party information.

    Args:
        party_details (dict): Dictionary containing all party details including:
            - celebrant_name
            - celebration_type
            - age (optional)
            - theme
            - interests
            - date
            - time
            - location
            - preferences (list)
            - style
            - emoji_level
            - length
            - gift_emphasis_level
            - custom_green_statement (optional)
            - cash_method (optional)
            - paypal_link (optional)
            - charity_link (optional)
    """
    # Handle custom celebration type
    celebration = party_details['celebration_type']
    if celebration.startswith('other:'):
        celebration = celebration.replace('other:', '').strip()

    # Handle custom theme
    theme = party_details['theme']
    if theme.startswith('other:'):
        theme = theme.replace('other:', '').strip()

    # Get gift preference instructions based on emphasis level
    gift_instructions = get_gift_emphasis_guide(
        party_details['gift_emphasis_level'],
        party_details['preferences'],
        party_details.get('custom_green_statement', ''),
        party_details.get('cash_method'),
        party_details.get('paypal_link'),
        party_details.get('charity_link')
    )

    # Create base prompt
    prompt = f"""Please write a {party_details['style']} invitation for a {celebration} celebration. Here are the details:

Celebrant: {party_details['celebrant_name']}
{"Age: " + party_details['age'] if party_details.get('age') else ""}
Theme: {theme}
Date: {party_details['date']}
Time: {party_details['time']}
Location: {party_details['location']}

{"Personal Interests: " + party_details['interests'] if party_details.get('interests') else ""}

{gift_instructions}

Style instruction: {get_style_guide(party_details['style'])}
Emoji instruction: {get_emoji_guide(party_details['emoji_level'])}
Length instruction: {get_length_guide(party_details['length'])}

Please write a warm and inviting message that incorporates the theme and personal interests naturally.
Format all dates, times, locations, and the celebrant's name using markdown bold syntax (e.g., **date**)."""

    # Call Claude API
    response = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=400,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text

def get_style_guide(style):
    """Return style instructions based on selected style."""
    guides = {
        'formal': "Write in a polite and formal tone, suitable for traditional celebrations",
        'friendly': "Write in a warm and welcoming tone, balancing professionalism with approachability",
        'very casual': "Write in a fun and casual tone, making the invitation feel personal and relaxed"
    }
    return guides.get(style, guides['friendly'])

def get_emoji_guide(level):
    """Return emoji usage instructions based on selected level."""
    guides = {
        'none': "Do not use any emojis",
        'minimal': "Use very few emojis (1-2) at key points",
        'moderate': "Use a moderate amount of emojis (3-5) throughout the text",
        'lots': "Use plenty of emojis throughout the text to make it fun and expressive"
    }
    return guides.get(level, guides['moderate'])

def get_length_guide(length):
    """Return word count ranges based on selected length."""
    guides = {
        'very-short': "Keep the response between 30-50 words",
        'short': "Keep the response between 50-75 words",
        'medium': "Keep the response between 100-150 words",
        'long': "Keep the response between 150-200 words"
    }
    return guides.get(length, guides['medium'])

def get_gift_emphasis_guide(level, preferences, custom_statement='', cash_method=None, paypal_link=None, charity_link=None):
    """Return gift preference instructions based on emphasis level and payment options."""
    preferences_text = ', '.join(preferences) if preferences else 'no specific preferences'

    # Add payment details if cash donations are included
    if 'cash donations welcome' in preferences and cash_method:
        if cash_method == 'envelope':
            preferences_text += ". Cash gifts should be presented in an envelope"
        elif cash_method == 'paypal' and paypal_link:
            preferences_text += f". PayPal contributions can be sent via: {paypal_link}"

    # Add charity details if included
    if 'charity donations welcome' in preferences and charity_link:
        preferences_text += f". In lieu of gifts, consider donating to our chosen charity at: {charity_link}"

    guides = {
        'subtle': f"""
Gift preference instruction: Mention these gift preferences very subtly and indirectly, as a gentle aside: {preferences_text}. 
Use soft language like "if you're thinking of gifts" or "has an appreciation for".""",

        'gentle': f"""
Gift preference instruction: Present these gift preferences as friendly suggestions: {preferences_text}.
Use warm, encouraging language like "would be delighted with" or "we warmly welcome".""",

        'clear': f"""
Gift preference instruction: State these gift preferences clearly but politely: {preferences_text}.
Use direct language like "we're requesting" or "please note that we prefer", while maintaining a warm tone.""",

        'eco': f"""
Gift preference instruction: Present these gift preferences as part of an environmental choice: {preferences_text}.
Include a brief mention of sustainability. Use clear, purposeful language about sustainable choices.
{custom_statement if custom_statement else ''}""",

        'advocate': f"""
Gift preference instruction: Frame these gift preferences within a strong environmental message: {preferences_text}.
{custom_statement if custom_statement else "Our family is committed to raising eco-conscious children and celebrating sustainably."}
Use clear, purposeful language about sustainable choices and environmental impact.
End the invitation with this footer: "Want to create your own sustainable celebration? Visit GreenVite.fun 🌱" """
    }
    return guides.get(level, guides['gentle'])