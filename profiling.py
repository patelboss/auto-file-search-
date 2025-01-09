import cProfile
import pstats
from io import StringIO
import logging
from pyrogram import Client, filters

def profile_function(function_to_profile):
    """
    Profiles a given function and returns the profiling result as a string.
    """
    profiler = cProfile.Profile()
    profiler.enable()  # Start profiling
    
    # Call the function to be profiled
    function_to_profile()
    
    profiler.disable()  # Stop profiling
    
    # Collect profiling stats and format output
    output = StringIO()
    stats = pstats.Stats(profiler, stream=output).sort_stats('cumulative')
    stats.print_stats()
    
    return output.getvalue()  # Return the profiling results as a string
@Client.on_message(filters.command("profile"))
async def profile_command(self, client, message):
        """
        Profile a function and return the results when /profile command is invoked.
        """
        # Call the profiling utility with the function to profile
    profile_result = profile_function(self.some_function_to_profile)

        # Send the profiling results to the user
    await message.reply_text(f"**Profiling Results:**\n{profile_result}")

