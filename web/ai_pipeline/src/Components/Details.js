import React from 'react';

import Accordion from '@material-ui/core/Accordion';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Typography from '@material-ui/core/Typography';

import Code from 'react-code-prettify';

import _ from 'lodash';

import classNames from 'classnames/bind';

import './Details.scss';

// import moment from 'moment';
// import _ from 'lodash';

import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
	heading: {
		fontSize: theme.typography.pxToRem(15),
		flexBasis: '33.33%',
		flexShrink: 0,
    },
	secondaryHeading: {
		fontSize: theme.typography.pxToRem(12),
		lineHeight: 1.75,
		color: theme.palette.text.secondary,
    },
    error: {
        color: theme.palette.error.light,
	},
    finished: {
        color: theme.palette.success.light,
	},
    code: {
        width: '100%',
    }
}));

function formatDate(date) {
	return date.format('YYYY-MM-DD HH:mm:ss.SSS');
}

function DetailsRender(props) {
	const classes = useStyles();

	const handleChange = (event, isExpanded) => {
		if (props.onChange) {
			props.onChange(event, isExpanded);
		}
	};

	if (!props.detail) {
		return <div></div>;
	}

    const classList1 = {};
	classList1[classes.heading] = true;
    classList1[classes.error] = props.detail.__is_error === 1;
    classList1[classes.finished] = props.detail.__is_finished === 1;
    const classList2 = {};
    classList2[classes.secondaryHeading] = true;
    classList1[classes.error] = props.detail.__is_error === 1;
    classList1[classes.finished] = props.detail.__is_finished === 1;

	const detail_repr = _.cloneDeep(props.detail)
	delete detail_repr._attachments;
	delete detail_repr._series;
	delete detail_repr._id;
    const codeString = JSON.stringify(detail_repr, null, 4);
	return (
		<Accordion expanded={props.expanded} onChange={handleChange}>
			<AccordionSummary expandIcon={<ExpandMoreIcon />}>
				<Typography className={classNames(classList1)}>{props.detail._stage}</Typography>
				<Typography className={classNames(classList2)}>{formatDate(props.detail.__create_date)}</Typography>
			</AccordionSummary>
			<AccordionDetails>
                <div className={classes.code + ' code-accordion'}>
				    <Code codeString={codeString} language="json" />
                </div>
			</AccordionDetails>
		</Accordion>
	);
}

export default DetailsRender;
