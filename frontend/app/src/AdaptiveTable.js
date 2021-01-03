import React from "react";
import Table from "react-bootstrap/Table";
import "bootstrap/dist/css/bootstrap.min.css";

class AdaptiveTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        rowData: [[[]]]
    }
  }
  render() {
    return (
      <Table variant="dark" striped bordered hover style={{ width: 700, float: "right" }} size="sm">
        <tbody>
        <tr>
          <th>SYMBOL</th>
          <th>Name of acquirer/disposer</th>
          <th>Value of security</th>
          <th>No. of securities</th>
          <th>Mode of acquisition</th>
          <th>Date of allotment</th>
          <th>Avg. txn price</th>
        </tr>
        
        {
            this.props.rowData.map((item) => (
                <tr onClick={() => this.setState({selectedRow : item[0]})}>
                    {item.map((val) => (
                    <td>{val}</td>
                    ))}
                </tr>
            ))
        }
        </tbody>

      </Table>
    );
  }
}
export default AdaptiveTable;
