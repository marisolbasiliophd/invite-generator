from anthropic import Anthropic
import os

# Initialize Anthropic client using environment variable
anthropic = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

# Theme-specific vocabulary and elements dictionary
THEME_ELEMENTS = {
    'superheroes': {
        'vocabulary': ['superhero', 'powers', 'mighty', 'heroic', 'adventure', 'save the day', 'mission', 'headquarters'],
        'elements': ['superhero costumes', 'special powers', 'hero training activities', 'saving the world'],
        'atmosphere': 'action-packed and heroic'
    },
    'princess': {
        'vocabulary': ['royal', 'magical', 'enchanted', 'kingdom', 'castle', 'crown', 'majestic', 'fairy tale'],
        'elements': ['royal castle', 'magical wands', 'tiaras', 'royal activities'],
        'atmosphere': 'magical and enchanting'
    },
    'dinosaurs': {
        'vocabulary': ['prehistoric', 'mighty', 'roaring', 'extinct', 'fossil', 'Jurassic', 'ancient'],
        'elements': ['dinosaur excavation', 'fossil hunting', 'prehistoric games', 'dino facts'],
        'atmosphere': 'prehistoric and adventurous'
    },
    'space': {
        'vocabulary': ['cosmic', 'stellar', 'galactic', 'astronomical', 'orbit', 'space station', 'mission control'],
        'elements': ['space exploration', 'astronaut training', 'planetary discovery', 'cosmic games'],
        'atmosphere': 'out-of-this-world and stellar'
    },
    'animals': {
        'vocabulary': ['wild', 'safari', 'jungle', 'habitat', 'species', 'conservation', 'nature'],
        'elements': ['animal spotting', 'wildlife games', 'nature exploration', 'animal facts'],
        'atmosphere': 'wild and naturalistic'
    },
    'pirates': {
        'vocabulary': ['ahoy', 'treasure', 'swashbuckling', 'maritime', 'seafaring', 'buccaneer', 'crew'],
        'elements': ['treasure hunt', 'ship activities', 'map reading', 'pirate games'],
        'atmosphere': 'adventurous and seafaring'
    },
    'unicorns': {
        'vocabulary': ['magical', 'rainbow', 'sparkle', 'enchanted', 'mystical', 'glitter', 'fairy'],
        'elements': ['rainbow activities', 'magical crafts', 'unicorn games', 'enchanted fun'],
        'atmosphere': 'magical and whimsical'
    },
    'sports': {
        'vocabulary': ['championship', 'victory', 'team', 'athletic', 'champion', 'score', 'win'],
        'elements': ['sports games', 'team activities', 'championship challenges', 'athletic fun'],
        'atmosphere': 'energetic and competitive'
    },
    'ocean': {
        'vocabulary': ['underwater', 'marine', 'aquatic', 'sea', 'coral', 'waves', 'deep blue'],
        'elements': ['underwater exploration', 'marine discovery', 'ocean games', 'sea life'],
        'atmosphere': 'underwater and mysterious'
    },
    'art': {
        'vocabulary': ['creative', 'artistic', 'colorful', 'imaginative', 'masterpiece', 'inspiration', 'design'],
        'elements': ['art creation', 'creative activities', 'artistic expression', 'crafting fun'],
        'atmosphere': 'creative and artistic'
    },
    'science': {
        'vocabulary': ['experiment', 'discovery', 'laboratory', 'hypothesis', 'research', 'innovation', 'scientist'],
        'elements': ['science experiments', 'lab activities', 'discovery stations', 'research fun'],
        'atmosphere': 'experimental and innovative'
    },
    'garden': {
        'vocabulary': ['botanical', 'natural', 'blooming', 'growing', 'organic', 'floral', 'nature'],
        'elements': ['garden exploration', 'planting activities', 'nature crafts', 'outdoor fun'],
        'atmosphere': 'natural and peaceful'
    },
    'videogames': {
        'vocabulary': ['gaming', 'level up', 'player', 'quest', 'achievement', 'victory', 'high score'],
        'elements': ['gaming stations', 'virtual challenges', 'player activities', 'game tournaments'],
        'atmosphere': 'gaming and competitive'
    },
    'music': {
        'vocabulary': ['musical', 'rhythmic', 'melodic', 'harmony', 'symphony', 'beat', 'tune'],
        'elements': ['music making', 'dance activities', 'rhythm games', 'musical fun'],
        'atmosphere': 'musical and rhythmic'
    },
    'circus': {
        'vocabulary': ['spectacular', 'carnival', 'amazing', 'performances', 'acrobatic', 'magnificent', 'show'],
        'elements': ['circus acts', 'carnival games', 'amazing performances', 'spectacular fun'],
        'atmosphere': 'spectacular and entertaining'
    }
}

def create_invite_text(party_details):
    """
    Generate party invite text using Claude API based on detailed party information.
    """
    # Handle custom celebration type
    celebration = party_details['celebration_type']
    if celebration.startswith('other:'):
        celebration = celebration.replace('other:', '').strip()

    # Handle theme with enhanced theme control
    theme = party_details['theme']
    if theme.startswith('other:'):
        theme = theme.replace('other:', '').strip()
        # Create custom theme elements for user-specified themes
        theme_info = {
            'vocabulary': ['special', 'unique', 'custom', 'themed', 'extraordinary'],
            'elements': ['themed activities', 'special games', 'unique experiences'],
            'atmosphere': 'unique and special'
        }
    else:
        theme_info = THEME_ELEMENTS.get(theme, THEME_ELEMENTS['art'])  # Default to art theme if not found

    # Get themed opening section with activities
    theme_section = create_theme_section(
        theme,
        theme_info,
        party_details['celebrant_name'],
        party_details.get('age', ''),
        party_details['date'],
        party_details['time'],
        party_details['location'],
        party_details.get('party_activities', '')
    )

    # Get interests and gifts section
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

    # Create enhanced prompt with strong theme enforcement
    prompt = f"""Create a {party_details['style']} invitation for a {celebration} celebration that MUST maintain a consistent {theme} theme throughout. The invitation should feel like a {theme_info['atmosphere']} experience.

Required theme elements to incorporate:
- Use at least 3 of these theme-specific words: {', '.join(theme_info['vocabulary'])}
- Include references to these themed elements: {', '.join(theme_info['elements'])}
- Maintain the {theme_info['atmosphere']} atmosphere throughout

Theme and Event Details:
{theme_section}

Interests and Gift Preferences:
{interests_and_gifts}

Style instruction: {get_style_guide(party_details['style'])}
Emoji instruction: {get_emoji_guide(party_details['emoji_level'])}
Length instruction: {get_length_guide(party_details['length'])}

Important formatting:
- Format all dates, times, locations, and the celebrant's name using markdown bold syntax (e.g., **date**)
- Create a flowing invitation without any section markers
- Make the first paragraph exciting and engaging
- Make the second paragraph feel personal and meaningful
- Ensure natural transitions between ideas
- MAINTAIN THE {theme.upper()} THEME THROUGHOUT THE ENTIRE INVITATION"""

    try:
        # Call Claude API with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = anthropic.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=400,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                continue

    except Exception as e:
        raise ValueError(f"Failed to generate invitation: {str(e)}")
def create_theme_section(theme, theme_info, name, age, date, time, location, activities=''):
    """Generate the themed opening paragraph including party activities if provided."""

    # Create theme-specific activity suggestions if none provided
    activities_text = f"""Include these special activities in an exciting way, maintaining the {theme} theme:
- {activities}""" if activities else f"""Suggest these theme-appropriate activities:
- {', '.join(theme_info['elements'][:2])}"""

    return f"""Create an exciting opening that:
- Uses {theme_info['atmosphere']} language throughout
- Incorporates at least 2 of these theme words: {', '.join(theme_info['vocabulary'][:4])}
- Announces that {name} {"turns " + age if age else "is celebrating"}
- Incorporates these details naturally while maintaining the theme:
  - Date: {date}
  - Time: {time}
  - Location: {location}
{activities_text}"""

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

    # Build interests text
    interests_intro = f"Given {name}'s love of {interests}" if interests else f"For {name}'s special day"

    emphasis_guides = {
        'subtle': f"""Create a warm paragraph that:
- Uses this context for gift suggestions: {interests_intro}
- Very subtly mentions these preferences: {preferences_text}
- Uses soft language like "if you're thinking of gifts" or "has an appreciation for" """,

        'gentle': f"""Create a warm paragraph that:
- Uses this context for gift suggestions: {interests_intro}
- Suggests these preferences gently: {preferences_text}
- Uses warm language like "would be delighted with" or "we warmly welcome" """,

        'clear': f"""Create a warm paragraph that:
- Uses this context for gift suggestions: {interests_intro}
- States these preferences clearly but politely: {preferences_text}
- Uses direct but warm language about the gift preferences""",

        'eco': f"""Create a warm paragraph that:
- Uses this context for gift suggestions: {interests_intro}
- Connects to environmental awareness where possible
- Presents these preferences as eco-conscious choices: {preferences_text}
{custom_statement if custom_statement else ''}""",

        'advocate': f"""Create a warm paragraph that:
- Uses this context for gift suggestions: {interests_intro}
- Connects strongly to environmental awareness
- Emphasizes sustainable gift choices: {preferences_text}
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