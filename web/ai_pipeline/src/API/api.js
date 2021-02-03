import axios from 'axios';
import _ from 'lodash';
import moment from 'moment';

// const server = 'http://127.0.0.1:5000/';
// const server = 'http://192.168.50.11:5000/';
const server = '/api/';

export default class API {
	// constructor() {}

	unpackData(data) {
		function customizer(value, name) {
			if (_.isObject(value) && value.__isDate === true) {
				return moment(value.__date);
			}
		}

		return _.cloneDeepWith(data, customizer);
	}

    get_detailed(transaction_id, done) {
        const that = this;
		axios
			.get(server + 'details/' + transaction_id)
			.then(function (response) {
                done(that.unpackData(response.data));
			})
			.catch(function (error) {
				//
				console.error(error);
			});
	}
	
	get_dcm_file_link(transaction_id, file_name) {
		return server + 'dcm/file/' + transaction_id + "/" + file_name;
	}

	get_dcm_data(transaction_id, file_name, done) {
		const that = this;
		axios
			.get(server + 'dcm/details/' + transaction_id + "/" + file_name)
			.then(function (response) {
                done(that.unpackData(response.data));
			})
			.catch(function (error) {
				//
				console.error(error);
			});
    }
    
	get_transactions(filter, done) {
		const that = this;
		axios
			.post(server + 'transactions', {
				filter,
			})
			.then(function (response) {
                done(that.unpackData(response.data));
			})
			.catch(function (error) {
				//
				console.error(error);
			});
	}
}
