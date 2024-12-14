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

    # Get interests and gift section combined
    interests_and_gifts = create_interests_and_gifts_section(
        party_details['celebrant_name'],
        party_details.get('interests', ''),
        party_details['gift_emphasis_level'],
        party_details['preferences'],
        party_details.get('custom_green_statement', ''),
        party_details.get('cash_method'),
        party_details.get('paypal_link'),
        party_details.get('charity_link')
    )

    # Create flowing prompt
    prompt = f"""Please write a {party_details['style']} invitation for a {celebration} celebration that flows naturally in two paragraphs:

Opening paragraph - theme and event details:
{theme_section}

Personal interests and gift preferences paragraph:
{interests_and_gifts}

Style instruction: {get_style_guide(party_details['style'])}
Emoji instruction: {get_emoji_guide(party_details['emoji_level'])}
Length instruction: {get_length_guide(party_details['length'])}

Important formatting:
- Format all dates, times, locations, and the celebrant's name using markdown bold syntax (e.g., **date**)
- Create a flowing invitation without any section numbers or headers
- Ensure natural transitions between ideas
- The second paragraph should flow smoothly from interests to gift preferences
- The gift preferences should feel connected to the child's interests where possible"""

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
    """Generate the themed opening paragraph."""
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
- Incorporates these details naturally:
  - Date: {date}
  - Time: {time}
  - Location: {location}"""

def create_interests_and_gifts_section(name, interests, emphasis_level, preferences, custom_statement='', cash_method=None, paypal_link=None, charity_link=None):
    """Generate combined interests and gift preferences section."""
    # Format gift preferences
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

    emphasis_guides = {
        'subtle': f"""Create a paragraph that:
- Warmly describes {name}'s interests: {interests}
- Very subtly mentions these gift preferences: {preferences_text}
- Uses soft language like "if you're thinking of gifts" or "has an appreciation for" """,

        'gentle': f"""Create a paragraph that:
- Warmly describes {name}'s interests: {interests}
- Suggests these gift preferences gently: {preferences_text}
- Uses warm language like "would be delighted with" or "we warmly welcome" """,

        'clear': f"""Create a paragraph that:
- Warmly describes {name}'s interests: {interests}
- States these gift preferences clearly but politely: {preferences_text}
- Uses direct but warm language about the gift preferences""",

        'eco': f"""Create a paragraph that:
- Warmly describes {name}'s interests: {interests}
- Connects interests to environmental awareness where possible
- Presents these gift preferences as eco-conscious choices: {preferences_text}
{custom_statement if custom_statement else ''}""",

        'advocate': f"""Create a paragraph that:
- Warmly describes {name}'s interests: {interests}
- Connects interests to environmental awareness
- Strongly emphasizes sustainable gift choices: {preferences_text}
{custom_statement if custom_statement else "Our family is committed to raising eco-conscious children and celebrating sustainably."}
End with: "Want to create your own sustainable celebration? Visit GreenVite.fun 🌱" """
    }

    return emphasis_guides.get(emphasis_level, emphasis_guides['gentle'])

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