from anthropic import Anthropic
import os

# Initialize Anthropic client using environment variable
anthropic = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

def create_invite_text(party_details):
    """
    Generate party invite text using Claude API based on detailed party information.
    """
    # Handle custom celebration type
    celebration = party_details['celebration_type']
    if celebration.startswith('other:'):
        celebration = celebration.replace('other:', '').strip()

    # Handle custom theme
    theme = party_details['theme']
    if theme.startswith('other:'):
        theme = theme.replace('other:', '').strip()

    # Get themed opening section
    theme_section = create_theme_section(
        theme,
        party_details['celebrant_name'],
        party_details.get('age', ''),
        party_details['date'],
        party_details['time'],
        party_details['location']
    )

    # Get personal section
    personal_section = create_personal_section(
        party_details['celebrant_name'],
        party_details.get('interests', '')
    )

    # Get gift section
    gift_section = get_gift_emphasis_guide(
        party_details['gift_emphasis_level'],
        party_details['preferences'],
        party_details.get('custom_green_statement', ''),
        party_details.get('cash_method'),
        party_details.get('paypal_link'),
        party_details.get('charity_link')
    )

    # Create structured prompt
    prompt = f"""Please write a {party_details['style']} invitation for a {celebration} celebration with three distinct sections:

Section 1 - Theme and Event Details:
{theme_section}

Section 2 - Personal Touch:
{personal_section}

Section 3 - Gift Preferences:
{gift_section}

Style instruction: {get_style_guide(party_details['style'])}
Emoji instruction: {get_emoji_guide(party_details['emoji_level'])}
Length instruction: {get_length_guide(party_details['length'])}

Important formatting:
- Format all dates, times, locations, and the celebrant's name using markdown bold syntax (e.g., **date**)
- Keep each section distinct but flowing naturally
- Ensure Section 1 captures attention with the theme
- Make Section 2 personal and warm
- Present Section 3 according to the gift emphasis level"""

    # Call Claude API
    response = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=400,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text

def create_theme_section(theme, name, age, date, time, location):
    """Generate the themed opening section."""
    theme_guides = {
        'superheroes': "Use superhero action and adventure themed language",
        'princess': "Use magical royal themed language",
        'dinosaurs': "Use prehistoric/dinosaur themed language",
        'space': "Use space exploration themed language",
        'animals': "Use safari/wildlife themed language",
        'pirates': "Use swashbuckling pirate themed language",
        'unicorns': "Use magical and enchanted themed language",
        'sports': "Use sports and championship themed language",
        'ocean': "Use underwater adventure themed language",
        'art': "Use creative and artistic themed language",
        'science': "Use laboratory and experiment themed language",
        'garden': "Use nature and flower themed language",
        'videogames': "Use gaming and adventure themed language",
        'music': "Use musical and rhythmic themed language",
        'circus': "Use carnival and circus themed language"
    }

    return f"""Create an exciting opening that:
- {theme_guides.get(theme, "Use theme-appropriate language")}
- Announces that {name} {"turns " + age if age else "is celebrating"}
- Incorporates these details in a thematic way:
  - Date: {date}
  - Time: {time}
  - Location: {location}
Make this section engaging and capture the theme's spirit."""

def create_personal_section(name, interests):
    """Generate the personal interests section."""
    if not interests:
        return f"Create a warm and welcoming message about {name}'s special day."

    return f"""Create a personal section that:
- Naturally introduces these interests: {interests}
- Shows what makes {name} special
- Creates a connection between the theme and their interests where possible
Make this section warm and personal."""

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
        'subtle': f"""Present these gift preferences ({preferences_text}) very subtly and indirectly.
Use soft language like "if you're thinking of gifts" or "has an appreciation for".""",

        'gentle': f"""Present these gift preferences ({preferences_text}) as friendly suggestions.
Use warm, encouraging language like "would be delighted with" or "we warmly welcome".""",

        'clear': f"""State these gift preferences ({preferences_text}) clearly but politely.
Use direct language like "we're requesting" or "please note that we prefer", while maintaining a warm tone.""",

        'eco': f"""Present these gift preferences ({preferences_text}) as part of an environmental choice.
Include a brief mention of sustainability. Use clear, purposeful language about sustainable choices.
{custom_statement if custom_statement else ''}""",

        'advocate': f"""Frame these gift preferences ({preferences_text}) within a strong environmental message.
{custom_statement if custom_statement else "Our family is committed to raising eco-conscious children and celebrating sustainably."}
Use clear, purposeful language about sustainable choices and environmental impact.
End the invitation with this footer: "Want to create your own sustainable celebration? Visit GreenVite.fun 🌱" """
    }
    return guides.get(level, guides['gentle'])