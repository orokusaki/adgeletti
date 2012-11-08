/*
 * @requires GPT library (e.g., //www.googletagservices.com/tag/js/gpt.js)
 */

// Set up a simple console noop for clients without a console
window.console = window.console || {log: function(m){}, error: function(m){}};


// Set up the `Adgeletti` object and its methods
window.Adgeletti = {
	// An object for storing data (populated upstream)
	data: {},

	// Sets up an ad position by adding it to the `data` object herein
	position: function(breakpoint, ad_unit_id, sizes, div_id){
		var positions = this.data[breakpoint] = this.data[breakpoint] || [];
		positions.push({
			ad_unit_id: ad_unit_id,
			sizes: sizes,
			div_id: div_id
		});
	},

	// Displays all ads in the page for the given breakpoint
	display: function(breakpoint){
		console.log('Displaying ads for breakpoint "' + breakpoint + '"');
		var positions = this.data.breakpoint || [];
        var num_positions = positions.length;

		if(num_positions == 0){  // Johnny 5
			console.log('No ads for breakpoint "' + breakpoint + '"');
			return;
		}

		for(var i = 0; i < num_positions; ++i){
			var pos = positions[i];
			googletag.pubads().display(pos.ad_unit_id, pos.sizes, pos.div_id);
		}
	}
}
