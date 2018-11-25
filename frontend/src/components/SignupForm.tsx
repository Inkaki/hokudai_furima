import React from 'react';
import PropTypes from 'prop-types';

interface IState {
  username: string,
  password: string,
}

interface IProps {
  handleSignup: (e:any, data:any) => void
}

class SignupForm extends React.Component<IProps, IState> {
  static propTypes = {
    handleSignup: PropTypes.func.isRequired
  };

  state = {
    username: '',
    password: ''
  };

  handleChange = (e:any) => {
    const name = e.target.name;
    const value = e.target.value;
    this.setState(prevstate => {
      const newState = { ...prevstate };
      newState[name] = value;
      return newState;
    });
  };

  render() {
    return (
      <form onSubmit={e => this.props.handleSignup(e, this.state)}>
        <h4>Sign Up</h4>
        <label htmlFor="username">Username</label>
        <input
          type="text"
          name="username"
          value={this.state.username}
          onChange={this.handleChange}
        />
        <label htmlFor="password">Password</label>
        <input
          type="password"
          name="password"
          value={this.state.password}
          onChange={this.handleChange}
        />
        <input type="submit" />
      </form>
    );
  }
}

export default SignupForm;