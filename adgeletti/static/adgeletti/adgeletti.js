// @requires GPT library (e.g., //www.googletagservices.com/tag/js/gpt.js)

// Set up a simple console noop for clients without a console
window.console = window.console || {log: function(m){}};


// Set up the `Adgeletti` object and its methods
window.Adgeletti = {
	// Data about the ads in a page
	data: {
		// A dictionary of ad positions, keyed by their respective breakpoints
		positions: {},
		// A dictionary of ad positions that are showing, keyed by their
		// respective breakpoints
		showing: {},
		// A dictionary of ad positions that have been displayed, keyed by
		// their respective breakpoints
		displayed: {}
	},

	// Sets up an ad position by adding it to `data.positions`
	position: function(breakpoint, ad_unit_id, sizes, div_id){
		var positions = this.data.positions[breakpoint] = this.data.positions[breakpoint] || [];
		positions.push({
			ad_unit_id: ad_unit_id,
			sizes: sizes,
			div_id: div_id
		});
	},

	// Displays all ads in the page for the given breakpoint
	display: function(breakpoint){
		console.log('Displaying ads for breakpoint "' + breakpoint + '"');

		// Ensure a list for the breakpoint in `data.displayed`
		var displayed = this.data.displayed[breakpoint] = this.data.displayed[breakpoint] || [];
		// Ensure a list for the breakpoint in `data.showing`
		var showing = this.data.showing[breakpoint] = this.data.showing[breakpoint] || [];
		// Get a list of positions for the breakpoint, or an empty list
		var positions = this.data.positions[breakpoint] || [];

		// Loop through the breakpoint's positions, showing each's div, and
		// using `googletag.pubads().display(...)` to display ones that haven't
		// already been displayed
		for(var i = 0; i < positions.length; ++i){
			var pos = positions[i];

			// Add the position to the list of showing positions, so that its
			// div can be hidden via `this.hide(...)`
			showing.push(pos);

			// Show the div and add it to `data.showing`
			console.log('Showing ad div #' + pos.div_id);
			document.getElementById(pos.div_id).style.display = 'block';

			// Check whether the ad has already been displayed
			for(var j = 0; j < displayed.length; j ++){
				if(displayed[j].div_id == pos.div_id){
					console.log('Ad ' + pos.ad_unit_id + ' already displayed for breakpoint "' + breakpoint + '"');
					return;
				}
			}

			// Add the position to the list of displayed positions
			displayed.push(pos);

			// Tell Google to display the ad
			console.log('Displaying ad ' + pos.ad_unit_id + ' for breakpoint "' + breakpoint + '"');
			googletag.pubads().display(pos.ad_unit_id, pos.sizes, pos.div_id);
		}
	},

	// Hides all the ads in the page for the given breakpoint
	hide: function(breakpoint){
		console.log('Hiding ads for breakpoint "' + breakpoint + '"');

		// Get a list of showing positions for the breakpoint, or an empty list
		var showing = this.data.showing[breakpoint] || [];
		for(var i = 0; i < showing.length; ++i){
			var pos = showing[i];

			// Hide the ad div
			console.log('Hiding ad div #' + pos.div_id);
			document.getElementById(pos.div_id).style.display = 'none';
		}

		// Reset the list of showing positions
		this.data.showing[breakpoint] = [];
	}
}
