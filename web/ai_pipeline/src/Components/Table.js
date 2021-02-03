import React from 'react';

// import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import LaunchIcon from '@material-ui/icons/Launch';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TablePagination from '@material-ui/core/TablePagination';
import Paper from '@material-ui/core/Paper';

import moment from 'moment';
import _ from 'lodash';

import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
	topSpace: {
		marginTop: 20,
	},
	table: {
		minWidth: 650,
	},
	emptyPadding: {
		marginTop: 20,
		padding: '10px 20px',
		opacity: 0.75,
	},
});

function formatValue(val) {
	if (moment.isMoment(val)) {
		return val.format('YYYY-MM-DD HH:mm');
	}
	if (_.isArray(val)) {
		let arr = '';
		_.forEach(_.sortBy(val), (v) => {
			if (arr.length > 0) {
				arr += ', ';
			}
			arr += v;
		});
		return arr;
	}
	return val;
}

function TableRender(props) {
	const classes = useStyles();

	let headers = props.data && props.data.header ? props.data.header : [];
	let rows = props.data && props.data.data ? props.data.data : [];

	let pages =
		props.data && props.data.pages
			? props.data.pages
			: {
					current: 0,
					max: 0,
					items: 0,
			  };

	const handleChangePage = (event, newPage) => {
		if (props.onChangePage) {
			props.onChangePage(event, newPage);
		}
	};
	const handleChangeRowsPerPage = (event) => {
		if (props.onChangeRowsPerPage) {
			props.onChangeRowsPerPage(event);
		}
	};

	const detailsClick = (row) => {
		return () => {
			if (props.onRowClick) {
				props.onRowClick(row);
			}
		};
	};

	return rows && rows.length > 0 ? (
		<TableContainer component={Paper} className={classes.topSpace}>
			<Table className={classes.table} size="small">
				<TableHead>
					<TableRow>
						{headers.map((header) => (
							<TableCell key={header.name}>{header.display}</TableCell>
						))}
						<TableCell align="right"></TableCell>
					</TableRow>
				</TableHead>

				<TableBody>
					{rows.map((row) => (
						<TableRow
							key={row._id}
							className={
								'pipeline-table-row' +
								(row.is_error ? ' row-error' : '') +
								(row.is_finished ? ' row-finished' : '')
							}
						>
							{headers.map((header) => (
								<TableCell key={header.name} className={header.name}>
									{formatValue(row[header.name])}
								</TableCell>
							))}

							<TableCell align="right">
								<IconButton onClick={detailsClick(row)}>
									<LaunchIcon />
								</IconButton>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
			{/* {pages.items > pages.max && ( */}
			<TablePagination
				rowsPerPageOptions={[5, 10, 25]}
				component="div"
				count={pages.items}
				rowsPerPage={pages.max}
				page={pages.current}
				onChangePage={handleChangePage}
				onChangeRowsPerPage={handleChangeRowsPerPage}
			/>
			{/* )} */}
		</TableContainer>
	) : (
		<Paper className={classes.emptyPadding} elevation={3}>
			No transactions found
		</Paper>
	);
}

export default TableRender;
