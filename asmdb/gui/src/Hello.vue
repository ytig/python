<template>
  <div class="hello-container">
    <div class="hello-grow"></div>
    <table class="hello-content">
      <tr>
        <td align="right">
          <span>platform</span>
        </td>
        <td>
          <input type="text" />
        </td>
      </tr>
      <tr>
        <td align="right">
          <span>process</span>
        </td>
        <td>
          <input type="text" />
        </td>
      </tr>
      <tr>
        <td align="right">
          <span>script</span>
        </td>
        <td>
          <input type="file" />
        </td>
      </tr>
    </table>
    <div class="hello-grow"></div>
  </div>
</template>

<script>
export default {
  methods: {
    startDebug: function() {
      document.body.webkitRequestFullScreen();
      this.$router.replace('/world');
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.hello-container {
  background: @color-background;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  .hello-grow {
    flex-grow: 1;
  }
  .hello-content {
    span {
      font-size: 16px;
      font-family: 'Wawati SC';
      color: @color-text;
      margin-right: 12px;
    }
    input {
      background: #fff;
      font-size: 12px;
    }
  }
}
</style>
