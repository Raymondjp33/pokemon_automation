// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stream_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StreamData _$StreamDataFromJson(Map<String, dynamic> json) => StreamData(
      away: json['away'] as bool,
    )
      ..switch1Content = json['left'] == null
          ? null
          : DisplayContent.fromJson(json['left'] as Map<String, dynamic>?)
      ..switch2Content = json['right'] == null
          ? null
          : DisplayContent.fromJson(json['right'] as Map<String, dynamic>?);

Map<String, dynamic> _$StreamDataToJson(StreamData instance) =>
    <String, dynamic>{
      'away': instance.away,
      'left': instance.switch1Content?.toJson(),
      'right': instance.switch2Content?.toJson(),
    };
