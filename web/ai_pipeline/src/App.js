import React, { useState, useEffect } from 'react';
import './App.scss';

import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import RefreshIcon from '@material-ui/icons/Refresh';
// import Link from '@material-ui/core/Link';
import Modal from '@material-ui/core/Modal';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';

// import { BrowserRouter as Router, Switch, Route, Link, useParams } from 'react-router-dom';
// import { BrowserRouter as Router, Switch, Route, useParams, useRouteMatch, useLocation, useHistory } from 'react-router-dom';
import { BrowserRouter as Router, Switch, Route, useParams, useHistory } from 'react-router-dom';

import _ from 'lodash';
import moment from 'moment';

import StydyTable from './Components/Table';
import Details from './Components/Details';
import Serie from './Components/Serie';

import API from './API/api';

import MomentUtils from '@date-io/moment';
// import "moment/locale/en";

import { MuiPickersUtilsProvider, KeyboardDateTimePicker } from '@material-ui/pickers';

import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import cornerstone from 'cornerstone-core';
import cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';
import cornerstoneMath from 'cornerstone-math';
import cornerstoneTools from 'cornerstone-tools';
import Hammer from 'hammerjs';
import dicomParser from 'dicom-parser';

import CornerstoneViewport from 'react-cornerstone-viewport';

import { makeStyles } from '@material-ui/core/styles';

const api = new API();

const useStyles = makeStyles((theme) => ({
	root: {
		flexGrow: 1,
	},
	menuButton: {
		marginRight: theme.spacing(2),
	},
	topSpacing: {
		marginTop: theme.spacing(2),
	},
	title: {
		flexGrow: 1,
	},
	filtersButton: {
		marginTop: 7,
	},
	detailsLabel: {
		marginBottom: 10,
	},
	backdrop: {
		zIndex: theme.zIndex.drawer + 1,
		color: '#fff',
	},
}));

function getCreated(details) {
	let detail = null;
	if (details) {
		_.forEach(details, (d) => {
			if (d._stage === 'created') {
				detail = d;
			}
		});
	}

	return detail;
}

let transactions_details_once = true;
function TransactionDetails() {
	const classes = useStyles();

	let { id } = useParams();

	const [expanded, setExpanded] = useState(false);
	const [detailsHistory, setDetailsHistory] = useState([]);
	const [openSingleDCM, setOpenSingleDCM] = useState(false);
	const [dataTableDCM, setDataTableDCM] = useState([]);
	const [openLoading, setOpenLoading] = useState(false);

	const [showTableDCM, setShowTableDCM] = useState(true);
	const [showImageDCM, setShowImageDCM] = useState(false);
	// const [showImageSeriesDCM, setShowImageSeriesDCM] = useState(false);
	const [imagesIds, setImagesIds] = useState([]);
	const [imageIdIndex, setImageIdIndex] = useState(0);

	const [selectedImage, setSelectedImage] = useState(null);

	const handleCloseSingleDCM = () => {
		setOpenSingleDCM(false);
	};

	// const openDCM = () => {
	// 	cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
	// 	cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

	// cornerstoneWADOImageLoader.configure({
	// 	beforeSend: function (xhr) {
	// 		// Add custom headers here (e.g. auth tokens)
	// 		//xhr.setRequestHeader('APIKEY', 'my auth token');
	// 	},
	// });

	// 	const imageId = 'wadouri:' + api.get_dcm_file_link(id, selectedImage.image.file_name);
	// 	if (cornerstoneElement != null) {
	// 		cornerstone.enable(cornerstoneElement);
	// 	}
	// 	cornerstone.loadImage(imageId).then((image) => {
	// 		if (cornerstoneElement != null) {
	// 			cornerstone.displayImage(cornerstoneElement, image);

	// 			setShowTableDCM(false);
	// 		}
	// 	});
	// };
	const openDCM = () => {
		if (showTableDCM) {
			setShowTableDCM(false);
			setShowImageDCM(true);

			// const imageId = 'wadouri:' + api.get_dcm_file_link(id, selectedImage.image.file_name);
			// console.log("serie", selectedImage.serie);
			// setImagesIds([imageId]);

			let selectedIndex = 0;

			const imageIds = [];
			let index = 0;
			_.forEach(selectedImage.serie, (se) => {
				if (selectedImage.image.file_name === se.file_name) {
					selectedIndex = index;
				}

				imageIds.push('wadouri:' + api.get_dcm_file_link(id, se.file_name));
				index++;
			});
			setImagesIds(imageIds);
			setImageIdIndex(selectedIndex);
		} else {
			setShowTableDCM(true);
			setShowImageDCM(false);
		}
	};

	useEffect(() => {
		if (transactions_details_once) {
			transactions_details_once = false;
			api.get_detailed(id, (data) => {
				setDetailsHistory(data.details);
			});
		}
	});

	const handlePanelChange = (panel) => (event, isExpanded) => {
		setExpanded(isExpanded ? panel : false);
	};

	const eventOpenSingleDCM = (singleImage, serie) => {
		setOpenLoading(true);
		setDataTableDCM([]);
		api.get_dcm_data(id, singleImage.file_name, (data) => {
			setDataTableDCM(data.dm);
			setOpenLoading(false);
			setOpenSingleDCM(true);

			setShowTableDCM(true);
			setShowImageDCM(false);
			setSelectedImage({
				image: singleImage,
				serie,
			});
		});
	};

	// const formatSeries = (singleDetails) => {
	// 	let rendered = [];
	// 	_.forEach(singleDetails._series, (serie, key) => {
	// 		let local_name = '';
	// 		let local_id = '';
	// 		_.forEach(serie, (s) => {
	// 			if (s.name) local_name = s.name;
	// 			if (s.id) local_id = s.id;
	// 		});
	// 		rendered.push(
	// 			<div className="dcm-serie">
	// 				<div className="dcm-serie-name">{local_name}</div>
	// 				<div className="dcm-serie-id">{local_id}</div>
	// 			</div>
	// 		);
	// 		_.forEach(serie, (s) => {
	// 			rendered.push(
	// 				<div className="dcm-serie-file-name">
	// 					<Link href="#" onClick={openSingleDCM(s, serie)}>
	// 						{s.file_name}
	// 					</Link>
	// 				</div>
	// 			);
	// 		});
	// 	});
	// 	return rendered;
	// };

	const singleDetails = getCreated(detailsHistory);
	return (
		<Container component="main" maxWidth="lg" fixed={true} className="main">
			<div style={{ marginTop: 20 }}></div>

			<Typography variant="h4" className={classes.detailsLabel}>
				Statuses and data
			</Typography>
			{detailsHistory.map((detail) => (
				<Details
					key={detail._id}
					detail={detail}
					expanded={expanded === detail._id}
					onChange={handlePanelChange(detail._id)}
				/>
			))}

			<div style={{ marginTop: 20 }}></div>
			<Typography variant="h4" className={classes.detailsLabel}>
				DICOM Files/Series
			</Typography>
			<div style={{ paddingBottom: 50 }}>
				<Serie data={singleDetails} onElementSelect={eventOpenSingleDCM} />
			</div>
			{/* <div>{singleDetails && formatSeries(singleDetails)}</div> */}
			<Backdrop className={classes.backdrop} open={openLoading}>
				<CircularProgress color="inherit" />
			</Backdrop>
			<div>
				<Modal open={openSingleDCM} onClose={handleCloseSingleDCM}>
					<div className="modal-body">
						<div class="dcm-data">
							<div class="dcm-data-content">
								{showTableDCM && (
									<div class="dcm-data-table">
										<TableContainer component={Paper}>
											<Table className={classes.table} size="small" aria-label="a dense table">
												<TableHead>
													<TableRow>
														<TableCell align="right">Name</TableCell>
														<TableCell align="left">Value</TableCell>
														<TableCell align="left">Tag</TableCell>
													</TableRow>
												</TableHead>
												<TableBody>
													{dataTableDCM &&
														dataTableDCM.map((row, i) => (
															<TableRow key={i}>
																<TableCell className="table-column-1" align="right">
																	{row.name}
																</TableCell>
																<TableCell className="table-column-2" align="left">
																	{row.value}
																</TableCell>
																<TableCell className="table-column-3" align="left">
																	{row.tag}
																</TableCell>
															</TableRow>
														))}
												</TableBody>
											</Table>
										</TableContainer>
									</div>
								)}
								{showImageDCM && (
									<div className="dcm-data-image">
										<CornerstoneViewport
											tools={[{ name: 'StackScrollMouseWheel', mode: 'active' }]}
											imageIds={imagesIds}
											imageIdIndex={imageIdIndex}
											// style={{ minWidth: '100%', height: '512px', flex: '1' }}
											style={{ minWidth: '100%', height: '100%', flex: '1' }}
										/>
									</div>
								)}
								{/* {showImageSeriesDCM && <div>IMAGE SERIES</div>} */}

								<div class="dcm-data-buttons">
									<ButtonGroup variant="contained" color="default">
										<Button onClick={openDCM}>
											{showTableDCM && 'Show IMAGE'}
											{showImageDCM && 'Show TABLE'}
										</Button>
										<Button onClick={handleCloseSingleDCM}>CLOSE</Button>
									</ButtonGroup>
								</div>
							</div>
						</div>
					</div>
				</Modal>
			</div>
		</Container>
	);
}

let transactions_once = true;
function Transactions() {
	const classes = useStyles();

	let startDateDefault = moment();
	// startDateDefault = startDateDefault.startOf('day').subtract(1, 'days');
	startDateDefault = startDateDefault.startOf('day');

	const [startDate, setStartDate] = useState(startDateDefault);
	const [endDate, setEndDate] = useState(null);
	const [tableData, setTableData] = useState(null);
	const [pagingData, setPagingData] = useState({
		current: 0, // current page
		max: 5, // items per page (DEFAULT 5)
	});

	const handleDateChange = (method) => {
		return (date) => method(date);
	};

	const refreshData = () => {
		api.get_transactions(
			{
				start: startDate ? startDate.toISOString() : null,
				end: endDate ? endDate.toISOString() : null,
				page: pagingData,
			},
			(data) => {
				_.forEach(data.trasactions, (obj, i) => {
					obj.__index = i + 1;
				});
				let tableDataDefinition = {
					header: [
						// { name: '_id', display: 'UID' },
						{ name: '__index', display: 'No' },
						{ name: 'stage', display: 'Stage' },
						// { name: 'is_error', display: 'is_error' },
						// { name: 'is_finished', display: 'is_finished' },
						{ name: 'last_update', display: 'Create Date' },
					],
					data: data.trasactions,
					pages: {
						current: pagingData.current, // current page
						max: pagingData.max, // items per page
						items: data.size, // items count
					},
				};

				_.forEach(data.fields, (field) => {
					tableDataDefinition.header.push({ name: field['display'], display: field['display'] });
				});

				setTableData(tableDataDefinition);
			}
		);
	};

	let history = useHistory();

	const rowDetailsClick = (row) => {
		transactions_once = true;
		transactions_details_once = true;
		history.push('/transaction/' + row._id);
	};

	useEffect(() => {
		if (transactions_once) {
			transactions_once = false;
			refreshData();
		}
	});

	const handleChangePage = (event, newPage) => {
		setPagingData({
			current: newPage,
			max: pagingData.max,
		});
		transactions_once = true;
		transactions_details_once = true;
	};
	const handleChangeRowsPerPage = (event) => {
		setPagingData({
			current: 0,
			max: parseInt(event.target.value, 10),
		});
		transactions_once = true;
		transactions_details_once = true;
	};

	return (
		<Container component="main" maxWidth="lg" fixed={true} className="main">
			<div style={{ marginTop: 20 }}></div>

			<MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils} locale="en">
				<Grid container justify="flex-start" alignItems="flex-start" spacing={2}>
					<Grid item xs={1}>
						Filters
					</Grid>
				</Grid>
				<Grid container justify="flex-start" alignItems="flex-start" spacing={2}>
					<Grid item xs={2}>
						<KeyboardDateTimePicker
							label="start date"
							// variant="inline"
							KeyboardButtonProps={{
								'aria-label': 'start date',
							}}
							value={startDate}
							format="YYYY-MM-DD HH:mm"
							onChange={handleDateChange(setStartDate)}
							autoOk={true}
							ampm={false}
						/>
					</Grid>
					<Grid item xs={2}>
						<KeyboardDateTimePicker
							label="end date"
							KeyboardButtonProps={{
								'aria-label': 'end date',
							}}
							value={endDate}
							format="YYYY-MM-DD HH:mm"
							clearable={true}
							onChange={handleDateChange(setEndDate)}
							autoOk={true}
							ampm={false}
						/>
					</Grid>
					<Grid item xs={2}>
						<IconButton
							edge="start"
							className={classes.filtersButton}
							color="secondary"
							aria-label="refresh"
							onClick={refreshData}
						>
							<RefreshIcon />
						</IconButton>
					</Grid>
				</Grid>
			</MuiPickersUtilsProvider>

			<StydyTable
				data={tableData}
				onRowClick={rowDetailsClick}
				onChangePage={handleChangePage}
				onChangeRowsPerPage={handleChangeRowsPerPage}
			/>
		</Container>
	);
}

let cornerstoneInit = false;

function App() {
	const classes = useStyles();

	if (!cornerstoneInit) {
		cornerstoneTools.external.cornerstone = cornerstone;
		cornerstoneTools.external.Hammer = Hammer;
		cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
		cornerstoneTools.init();

		cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
		cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
		cornerstoneWADOImageLoader.webWorkerManager.initialize({
			maxWebWorkers: navigator.hardwareConcurrency || 1,
			startWebWorkersOnDemand: true,
			taskConfiguration: {
				decodeTask: {
					initializeCodecsOnStartup: false,
					usePDFJS: false,
					strict: false,
				},
			},
		});
		cornerstoneInit = true;
	}

	const darkTheme = createMuiTheme({
		palette: {
			type: 'dark',
		},
	});

	const goHome = () => {
		window.location = '/';
	};

	return (
		<ThemeProvider theme={darkTheme}>
			<CssBaseline />
			<AppBar position="static">
				<Toolbar>
					<IconButton
						edge="start"
						className={classes.menuButton}
						color="inherit"
						aria-label="menu"
						onClick={goHome}
					>
						<MenuIcon />
					</IconButton>
					<Typography variant="h6" className={classes.title}>
						Transactions
					</Typography>
					{/* <Button color="inherit">Login</Button> */}
				</Toolbar>
			</AppBar>

			<Router>
				<Switch>
					<Route path="/transaction/:id">
						<TransactionDetails />
					</Route>
					<Route path="/">
						<Transactions />
					</Route>
				</Switch>
			</Router>
		</ThemeProvider>
	);
}

export default App;
