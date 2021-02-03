import React from 'react';

import Accordion from '@material-ui/core/Accordion';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';

import { makeStyles } from '@material-ui/core/styles';

import _ from 'lodash';

import './Details.scss';

const useStyles = makeStyles((theme) => ({
	heading: {
		fontSize: theme.typography.pxToRem(15),
		flexBasis: '33.33%',
		flexShrink: 0,
	},
	headingCount: {
		fontSize: theme.typography.pxToRem(12),
		color: theme.palette.text.secondary,
		marginLeft: 10,
	},
	secondaryHeading: {
		fontSize: theme.typography.pxToRem(12),
		lineHeight: 1.75,
		color: theme.palette.text.secondary,
	},
	error: {
		color: theme.palette.error.light,
	},
	code: {
		width: '100%',
		backgroundColor: '#1d1f21',
		padding: '10px 20px',
	},
}));

function SerieRender(props) {
	const classes = useStyles();

	const handleChange = (event, isExpanded) => {
		if (props.onChange) {
			props.onChange(event, isExpanded);
		}
	};

	const handleSelectEvent = (singleImage, serie) => (event) => {
		event.preventDefault();
		if (props.onElementSelect) {
			props.onElementSelect(singleImage, serie);
		}
	};

	if (!props.data || !props.data._series) {
		return <div></div>;
	}

	let rendered = [];
	_.forEach(props.data._series, (serie, key) => {
		let local_name = '';
		let local_id = '';
		_.forEach(serie, (s) => {
			if (s.name) local_name = s.name;
			if (s.id) local_id = s.id;
		});

		function zeroPad(num, places) {
			var zero = places - num.toString().length + 1;
			return Array(+(zero > 0 && zero)).join('0') + num;
		}

		let elements = [];
		_.forEach(serie, (s, idx) => {
			elements.push(
				<div className="serie-link">
					<Link color="textPrimary" href="#" onClick={handleSelectEvent(s, serie)}>
						<span className="serie-index">{zeroPad(idx + 1, 4)}:</span> {s.file_name}
					</Link>
				</div>
			);
		});

		rendered.push(
			<Accordion expanded={props.expanded} onChange={handleChange}>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					<Typography className={classes.heading}>
						{local_name}
						<span className={classes.headingCount}>({serie.length})</span>
					</Typography>
					<Typography className={classes.secondaryHeading}>{local_id}</Typography>
				</AccordionSummary>
				<AccordionDetails>
					<div className={classes.code + ' code-accordion'}>{elements}</div>
				</AccordionDetails>
			</Accordion>
		);
	});

	return rendered;
}

export default SerieRender;
